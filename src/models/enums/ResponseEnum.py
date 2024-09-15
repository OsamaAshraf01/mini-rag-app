from enum import Enum

class ResponseEnum(Enum):
    FILE_TYPE_NOT_SUPPORTED = "file_type_not_supported"
    FILE_SIZE_EXEEDED = "file_size_exeeded"
    FILE_UPLOAD_SUCCESS = "file_uploaded_succefully"
    FILE_UPLOAD_FAILED = "file_uploading_failed"

    PROCESSING_SUCCESS = "processing_success"
    PROCESSING_FAILED = "processing_failed"
    FILE_NOT_FOUND = "file_not_found"

    INVALID_ID = "invalid_file_id"
    PROJECT_NOT_FOUND = "project_not_found"

    INSERT_INTO_VECTORDB_SUCCESS = "insert_into_vectordb_success"
    VECTORDB_COLLECTION_RETRIEVED = "vectordb_collection_retrieved"

    INVALID_QUERY = "invalid_query"
    SEARCH_ERROR = "search_error"
    SEARCH_SUCCESS = "search_success"
