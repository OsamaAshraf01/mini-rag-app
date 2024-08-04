from enum import Enum

class ResponseSignal(Enum):
    FILE_TYPE_NOT_SUPPORTED = "file_type_not_supported"
    FILE_SIZE_EXEEDED = "file_size_exeeded"
    FILE_UPLOAD_SUCCESS = "file_uploaded_succefully"
    FILE_UPLOAD_FAILED = "file_uploading_failed"