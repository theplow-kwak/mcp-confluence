import requests
import datetime
import sys

# --- 설정 ---
MCP_SERVER_URL = "http://127.0.0.1:8000"
TARGET_LABEL = "auto-update"  # 검색할 라벨
UPDATE_MESSAGE = f"\n<p><em>(이 페이지는 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}에 자동 스크립트로 업데이트되었습니다.)</em></p>"
# --- 설정 끝 ---

def search_pages_by_label(label: str) -> list:
    """MCP 서버를 통해 특정 라벨을 가진 페이지를 검색합니다."""
    print(f"'{label}' 라벨을 가진 페이지를 검색합니다...")
    cql = f'label="{label}"'
    # 업데이트를 위해 본문(body)과 버전(version) 정보를 함께 요청합니다.
    expand = "body.storage,version"
    
    try:
        response = requests.get(
            f"{MCP_SERVER_URL}/pages/search",
            params={"cql": cql, "expand": expand}
        )
        response.raise_for_status()
        
        data = response.json()
        pages = data.get("results", [])
        
        if not pages:
            print("결과: 해당 라벨을 가진 페이지를 찾을 수 없습니다.")
            return []
            
        print(f"결과: {len(pages)}개의 페이지를 찾았습니다.")
        return pages
        
    except requests.exceptions.RequestException as e:
        print(f"오류: MCP 서버에 연결할 수 없습니다. ({e})")
        sys.exit(1)

def update_page_content(page_id: str, title: str, current_content: str, version: int):
    """MCP 서버를 통해 페이지 내용을 업데이트합니다."""
    print(f"  -> 페이지 ID {page_id} ('{title}') 업데이트 중...")
    
    new_content = current_content + UPDATE_MESSAGE
    payload = {
        "title": title,
        "content": new_content,
        "version": version
    }
    
    try:
        response = requests.put(
            f"{MCP_SERVER_URL}/pages/{page_id}",
            json=payload
        )
        response.raise_for_status()
        print(f"  -> 성공: 페이지가 성공적으로 업데이트되었습니다.")
        
    except requests.exceptions.HTTPError as e:
        print(f"  -> 실패: 페이지 업데이트 중 오류 발생 (상태 코드: {e.response.status_code})")
        print(f"     응답: {e.response.text}")
    except requests.exceptions.RequestException as e:
        print(f"  -> 실패: MCP 서버 통신 오류 ({e})")

def main():
    """메인 실행 함수"""
    pages_to_update = search_pages_by_label(TARGET_LABEL)
    
    if not pages_to_update:
        return

    for page in pages_to_update:
        update_page_content(
            page['id'],
            page['title'],
            page['body']['storage']['value'],
            page['version']['number']
        )

if __name__ == "__main__":
    main()