"""
OpenAI의 함수 호출(Function Calling)을 위한 도구 스키마 정의.
"""

search_pages_tool = {
    "type": "function",
    "function": {
        "name": "search_pages",
        "description": "CQL(Confluence Query Language)을 사용하여 Confluence 페이지를 검색합니다. 페이지 내용과 버전 정보도 함께 가져옵니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "cql": {
                    "type": "string",
                    "description": "검색에 사용할 CQL 쿼리. 예: 'space = \"DEV\" and title ~ \"회의록\" and created > \"2024-01-01\"'",
                }
            },
            "required": ["cql"],
        },
    }
}

create_page_tool = {
    "type": "function",
    "function": {
        "name": "create_page",
        "description": "Confluence에 새로운 페이지를 생성합니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "space_key": {"type": "string", "description": "페이지를 생성할 Confluence 스페이스의 키. 예: 'DEV'"},
                "title": {"type": "string", "description": "새 페이지의 제목"},
                "content": {"type": "string", "description": "HTML 형식의 페이지 본문 내용"},
                "parent_id": {"type": "string", "description": "부모 페이지의 ID. 지정하지 않으면 최상위 페이지로 생성됩니다."},
            },
            "required": ["space_key", "title", "content"],
        },
    }
}

update_page_tool = {
    "type": "function",
    "function": {
        "name": "update_page",
        "description": "ID로 특정 Confluence 페이지의 제목이나 내용을 업데이트합니다. 안전한 업데이트를 위해서는 반드시 현재 버전 번호를 함께 제공해야 합니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "page_id": {"type": "string", "description": "업데이트할 페이지의 ID"},
                "title": {"type": "string", "description": "새로운 페이지 제목"},
                "content": {"type": "string", "description": "HTML 형식의 새로운 페이지 본문 내용"},
                "version": {"type": "integer", "description": "업데이트의 기반이 되는 현재 페이지의 버전 번호."},
            },
            "required": ["page_id", "title", "content", "version"],
        },
    }
}

draft_summary_report_tool = {
    "type": "function",
    "function": {
        "name": "draft_summary_report",
        "description": "주어진 조건으로 여러 페이지를 검색하고 내용을 요약하여, 사용자 검토를 위한 보고서 초안(draft)을 생성합니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "cql": {"type": "string", "description": "요약할 페이지들을 찾기 위한 CQL 쿼리."},
                "space_key": {"type": "string", "description": "요약 보고서 페이지를 생성할 스페이스 키."},
                "report_title": {"type": "string", "description": "생성될 요약 보고서의 제목."},
                "summary_prompt": {"type": "string", "description": "요약의 세부 요구사항."},
            },
            "required": ["cql", "space_key", "report_title", "summary_prompt"],
        },
    }
}

confluence_tools_openai = [search_pages_tool, create_page_tool, update_page_tool, draft_summary_report_tool]