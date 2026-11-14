import logging
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app.config.db import get_collection
from app.models.chat import ConversationDB, MessageDB
from app.schemas.chat import ConversationCreate, ConversationResponse, MessageCreate, MessageResponse
from app.services.security import get_current_active_user
from app.services.fraud_detection import analyze_chat_message
from bson import ObjectId

logger = logging.getLogger("trust_sell.chat")
router = APIRouter(prefix="/chat", tags=["Secure Chat"])


def _format_time(dt: datetime) -> str:
    return dt.strftime("%I:%M %p") if dt else "Just now"


def _avatar_from_name(name: str) -> str:
    parts = name.split()
    return "".join(p[0] for p in parts[:2]).upper() if parts else "TS"


@router.get("/conversations", response_model=List[ConversationResponse])
async def list_conversations(current_user: dict = Depends(get_current_active_user)):
    col = get_collection("conversations")
    uid = current_user["_id"]
    cursor = col.find({"participant_ids": uid}).sort("last_message_at", -1)
    results = []
    async for conv in cursor:
        other_idx = 1 if conv["participant_ids"][0] == uid else 0
        other_name = conv["participant_names"][other_idx]
        results.append(
            ConversationResponse(
                _id=str(conv["_id"]),
                name=other_name,
                avatar=_avatar_from_name(other_name),
                preview=conv.get("last_message", ""),
                time=_format_time(conv.get("last_message_at")),
                listing_id=conv.get("listing_id"),
                listing_title=conv.get("listing_title"),
                participant_ids=conv["participant_ids"],
            )
        )
    return results


@router.post("/conversations", response_model=ConversationResponse, status_code=201)
async def start_conversation(
    payload: ConversationCreate,
    current_user: dict = Depends(get_current_active_user),
):
    if payload.participant_id == current_user["_id"]:
        raise HTTPException(status_code=400, detail="Cannot chat with yourself.")

    users_col = get_collection("users")
    other = await users_col.find_one({"_id": ObjectId(payload.participant_id)})
    if not other:
        raise HTTPException(status_code=404, detail="User not found.")

    conv_col = get_collection("conversations")
    existing = await conv_col.find_one(
        {
            "participant_ids": {"$all": [current_user["_id"], payload.participant_id]},
            "listing_id": payload.listing_id,
        }
    )
    if existing:
        conv_id = str(existing["_id"])
    else:
        listing_title = None
        if payload.listing_id:
            listing = await get_collection("listings").find_one(
                {"_id": ObjectId(payload.listing_id)}
            )
            listing_title = listing.get("title") if listing else None

        conv = ConversationDB(
            participant_ids=[current_user["_id"], payload.participant_id],
            participant_names=[current_user["name"], other["name"]],
            listing_id=payload.listing_id,
            listing_title=listing_title,
        )
        ins = await conv_col.insert_one(conv.to_dict())
        conv_id = str(ins.inserted_id)

    if payload.initial_message:
        await _persist_message(conv_id, payload.initial_message, current_user)

    conv = await conv_col.find_one({"_id": ObjectId(conv_id)})
    other_idx = 1 if conv["participant_ids"][0] == current_user["_id"] else 0
    return ConversationResponse(
        _id=conv_id,
        name=conv["participant_names"][other_idx],
        avatar=_avatar_from_name(conv["participant_names"][other_idx]),
        preview=conv.get("last_message", ""),
        time=_format_time(conv.get("last_message_at")),
        listing_id=conv.get("listing_id"),
        listing_title=conv.get("listing_title"),
        participant_ids=conv["participant_ids"],
    )


@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    conversation_id: str,
    current_user: dict = Depends(get_current_active_user),
):
    if not ObjectId.is_valid(conversation_id):
        raise HTTPException(status_code=400, detail="Invalid conversation id.")

    conv = await get_collection("conversations").find_one({"_id": ObjectId(conversation_id)})
    if not conv or current_user["_id"] not in conv["participant_ids"]:
        raise HTTPException(status_code=403, detail="Access denied.")

    msg_col = get_collection("messages")
    cursor = msg_col.find({"conversation_id": conversation_id}).sort("created_at", 1)
    out = []
    async for msg in cursor:
        msg_type = "sent" if msg["sender_id"] == current_user["_id"] else "received"
        out.append(
            MessageResponse(
                _id=str(msg["_id"]),
                conversation_id=conversation_id,
                sender_id=msg["sender_id"],
                sender_name=msg["sender_name"],
                text=msg["text"],
                type=msg_type,
                fraud_risk_score=msg.get("fraud_risk_score", 0),
                fraud_flags=msg.get("fraud_flags", []),
                blocked=msg.get("blocked", False),
                time=_format_time(msg.get("created_at")),
                created_at=msg.get("created_at"),
            )
        )
    return out


async def _persist_message(conversation_id: str, text: str, current_user: dict) -> MessageResponse:
    analysis = analyze_chat_message(text)
    if analysis.blocked:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Message blocked by TrustSell Escrow Fraud Filter.",
                "flags": analysis.flags,
                "risk_score": analysis.risk_score,
            },
        )

    msg = MessageDB(
        conversation_id=conversation_id,
        sender_id=current_user["_id"],
        sender_name=current_user["name"],
        text=text,
        fraud_risk_score=analysis.risk_score,
        fraud_flags=analysis.flags,
        blocked=False,
    )
    msg_col = get_collection("messages")
    ins = await msg_col.insert_one(msg.to_dict())

    await get_collection("conversations").update_one(
        {"_id": ObjectId(conversation_id)},
        {"$set": {"last_message": text[:120], "last_message_at": datetime.utcnow()}},
    )

    return MessageResponse(
        _id=str(ins.inserted_id),
        conversation_id=conversation_id,
        sender_id=current_user["_id"],
        sender_name=current_user["name"],
        text=text,
        type="sent",
        fraud_risk_score=analysis.risk_score,
        fraud_flags=analysis.flags,
        time=_format_time(datetime.utcnow()),
        created_at=datetime.utcnow(),
    )


@router.post("/conversations/{conversation_id}/messages", response_model=MessageResponse)
async def send_message(
    conversation_id: str,
    payload: MessageCreate,
    current_user: dict = Depends(get_current_active_user),
):
    if not ObjectId.is_valid(conversation_id):
        raise HTTPException(status_code=400, detail="Invalid conversation id.")

    conv = await get_collection("conversations").find_one({"_id": ObjectId(conversation_id)})
    if not conv or current_user["_id"] not in conv["participant_ids"]:
        raise HTTPException(status_code=403, detail="Access denied.")

    return await _persist_message(conversation_id, payload.text, current_user)
