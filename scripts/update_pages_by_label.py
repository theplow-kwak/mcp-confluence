import os
import sys
import asyncio
from dotenv import load_dotenv

# 프로젝트 루트 경로를 sys.path에 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.confluence_service import ConfluenceService
from app.services.llm_factory import get_llm_service
from app.models.confluence_models import PageUpdate

async def main(label: str, prompt: str):
    """
    지정된 레이블을 가진 모든 Confluence 페이지를 찾아 LLM으로 내용을 비동기적으로 업데이트합니다.
    """
    load_dotenv()
    
    confluence_service = ConfluenceService()
    llm_service = get_llm_service()

    print(f"'{label}' 레이블을 가진 페이지를 검색합니다...")
    # CQL을 사용하여 레이블로 페이지 검색
    pages = await confluence_service.search_pages(cql=f"label='{label}'")

    if not pages:
        print("해당 레이블을 가진 페이지를 찾을 수 없습니다.")
        return

    print(f"{len(pages)}개의 페이지를 찾았습니다. 내용을 업데이트합니다.")

    for page_summary in pages:
        page_id = page_summary['id']
        title = page_summary['title']
        
        print(f"  - '{title}' (ID: {page_id}) 페이지 업데이트 중...")
        
        # 현재 페이지의 전체 정보를 가져옵니다. (본문 내용 포함)
        current_page = await confluence_service.get_page(page_id, expand="body.storage,version")
        current_content = current_page['body']['storage']['value']
        
        # LLM을 사용하여 새 콘텐츠 생성
        # llm_service.process_query가 비동기이므로 await 사용
        full_prompt = f"{prompt}\n\n---\n\n기존 내용:\n{current_content}"
        llm_response = await llm_service.process_query(full_prompt)
        new_content = llm_response.get("response", "") # 응답 형식에 따라 수정 필요

        if not new_content:
            print(f"    ...LLM으로부터 유효한 콘텐츠를 받지 못해 건너뜁니다.")
            continue
        
        # 페이지 업데이트 모델 생성
        update_data = PageUpdate(title=title, content=new_content)
        
        # 페이지 업데이트 (update_page가 비동기이므로 await 사용)
        await confluence_service.update_page(page_id, update_data)
        
        print(f"    ...완료.")

    print("\n모든 페이지 업데이트가 완료되었습니다.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("사용법: python update_pages_by_label.py <label> <prompt>")
        sys.exit(1)
    
    label_arg = sys.argv[1]
    prompt_arg = sys.argv[2]
    # 비동기 main 함수 실행
    asyncio.run(main(label_arg, prompt_arg))