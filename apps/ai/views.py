import json

from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .models import ChatMessage, ChatSession
from .services import chat_stream


@csrf_exempt
@require_POST
def chat_stream_view(request):
    """SSE 流式对话接口。"""
    if not request.user.is_authenticated:
        return JsonResponse({"error": "未登录"}, status=401)

    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "无效的 JSON"}, status=400)

    session_id = body.get("session_id")
    user_content = body.get("content", "").strip()
    if not user_content:
        return JsonResponse({"error": "消息不能为空"}, status=400)

    if len(user_content) > 2000:
        return JsonResponse({"error": "消息过长，最多 2000 字符"}, status=400)

    # 获取或创建会话
    if session_id:
        session = ChatSession.objects.filter(id=session_id, user=request.user).first()
        if not session:
            return JsonResponse({"error": "会话不存在"}, status=404)
    else:
        title = user_content[:20] + ("..." if len(user_content) > 20 else "")
        session = ChatSession.objects.create(user=request.user, title=title)

    # 保存用户消息
    ChatMessage.objects.create(session=session, role=ChatMessage.Role.USER, content=user_content)

    # 构建历史消息（最近 20 条）
    history = list(
        session.messages.order_by("-created_at")[:20].values("role", "content")
    )
    history.reverse()

    def event_stream():
        full_response = []
        for token in chat_stream(request.user, history):
            # 检查是否是错误消息（JSON 格式且包含 error 字段）
            try:
                parsed = json.loads(token)
                if "error" in parsed:
                    yield f"data: {json.dumps({'error': parsed['error']}, ensure_ascii=False)}\n\n"
                    return
            except (json.JSONDecodeError, TypeError):
                pass

            full_response.append(token)
            yield f"data: {json.dumps({'token': token, 'session_id': session.id}, ensure_ascii=False)}\n\n"

        # 保存 AI 回复
        ai_content = "".join(full_response)
        if ai_content:
            ChatMessage.objects.create(
                session=session, role=ChatMessage.Role.ASSISTANT, content=ai_content
            )

        yield f"data: {json.dumps({'done': True, 'session_id': session.id}, ensure_ascii=False)}\n\n"

    response = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"
    return response


@require_GET
def chat_sessions_view(request):
    """获取当前用户的会话列表。"""
    if not request.user.is_authenticated:
        return JsonResponse({"error": "未登录"}, status=401)

    sessions = ChatSession.objects.filter(user=request.user).values(
        "id", "title", "created_at", "updated_at"
    )
    return JsonResponse(list(sessions), safe=False, json_dumps_params={"ensure_ascii": False})


@csrf_exempt
@require_POST
def chat_session_create_view(request):
    """新建会话。"""
    if not request.user.is_authenticated:
        return JsonResponse({"error": "未登录"}, status=401)

    session = ChatSession.objects.create(user=request.user)
    return JsonResponse({"id": session.id, "title": session.title})


@require_GET
def chat_session_detail_view(request, pk):
    """获取某会话的历史消息。"""
    if not request.user.is_authenticated:
        return JsonResponse({"error": "未登录"}, status=401)

    session = ChatSession.objects.filter(id=pk, user=request.user).first()
    if not session:
        return JsonResponse({"error": "会话不存在"}, status=404)

    messages = list(
        session.messages.values("role", "content", "created_at")
    )
    return JsonResponse(
        {"session_id": session.id, "title": session.title, "messages": messages},
        safe=False,
        json_dumps_params={"ensure_ascii": False},
    )


@csrf_exempt
@require_POST
def chat_session_delete_view(request, pk):
    """删除会话。"""
    if not request.user.is_authenticated:
        return JsonResponse({"error": "未登录"}, status=401)

    session = ChatSession.objects.filter(id=pk, user=request.user).first()
    if not session:
        return JsonResponse({"error": "会话不存在"}, status=404)

    session.delete()
    return JsonResponse({"ok": True})
