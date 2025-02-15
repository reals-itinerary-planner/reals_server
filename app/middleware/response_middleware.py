from typing import Union
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import StreamingResponse
from ..schemas.response_schema import ResponseSchema, serialize_object
import json


class ResponseMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Union[Response, JSONResponse]:
        response = await call_next(request)
        print("ResponseMiddleware is", response)
        # Handle streaming response
        if isinstance(response, StreamingResponse):
            # Collect all chunks into one response
            chunks = []
            async for chunk in response.body_iterator:
                chunks.append(chunk)
            content = b"".join(chunks).decode()

            try:
                # Parse the content as JSON
                json_content = json.loads(content)
                # print("json_content is 1", json_content, content, type(content))
                # If not already in our standard format
                if not all(
                    key in json_content for key in ["result", "status_code", "message"]
                ):
                    # print("json_content is", json_content, content, type(content))
                    # Create standardized response
                    standardized_response = ResponseSchema(
                        result=serialize_object(json_content),
                        status=response.status_code,
                        message="Success" if response.status_code < 400 else "Error",
                    ).dict()

                    # Convert to bytes and get content length
                    body = json.dumps(standardized_response).encode("utf-8")
                    headers = dict(response.headers)
                    headers["content-length"] = str(len(body))

                    return Response(
                        content=body,
                        status_code=response.status_code,
                        headers=headers,
                        media_type="application/json",
                    )

                # If already standardized, return as Response
                body = json.dumps(json_content).encode("utf-8")
                headers = dict(response.headers)
                headers["content-length"] = str(len(body))

                return Response(
                    content=body,
                    status_code=response.status_code,
                    headers=headers,
                    media_type="application/json",
                )

            except Exception as e:
                print(f"Error in response middleware: {e}")
                # If any error occurs during standardization, return original content
                body = content.encode("utf-8")
                headers = dict(response.headers)
                headers["content-length"] = str(len(body))

                return Response(
                    content=body,
                    status_code=response.status_code,
                    headers=headers,
                    media_type="application/json",
                )

        return response
