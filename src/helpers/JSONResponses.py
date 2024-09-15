from fastapi import status
from fastapi.responses import JSONResponse

class JSONResponses:
    @classmethod
    def BAD_REQUEST(cls, msg):
        return JSONResponse(
            status_code= status.HTTP_400_BAD_REQUEST,
            content= {
                "signal": msg
            }
        )
    

    @classmethod
    def OK(cls, content: dict):
        return JSONResponse(
            content= content
        )

