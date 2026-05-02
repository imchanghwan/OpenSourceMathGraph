# OpenSourceMathGraph

코드파일 + 빌드파일(exe)


**사용한 오픈 소스 라이브러리**

사용한 오픈소스 라이브러리 : pyqtgraph(그래프 렌더), PySide6(GUI), sympy(수식 파싱), numpy(그래프 배열 계산), pyinstaller(exe 빌드)


수식 추가 버튼

색상, 수식, 삭제, 표시 기능

```
그래프 패널 마우스 조작 가능

줌 인/아웃 : 휠

이동 : 클릭 후 드래그

x, y 축 스케일 조정 : 왼쪽, 하단에 마우스 커서 두고 휠
```

---

**전체 구조 정리**

**아키텍처 흐름**

```
ExpressionItemWidget
    ↓ Signal (데이터만)
ExpressionListPanel
    ↓ Signal (id + 데이터)
MainWindow
    ↓ connect
GraphController
    ↓ 계산 요청        ↓ 렌더링 요청
GraphItem          GraphPanel
(파싱 + 계산)      (curve 관리)
```

---

**각 클래스 책임**

| 클래스 | 책임 |
| --- | --- |
| `ExpressionItemWidget` | 입력 UI, 데이터만 Signal 발신 |
| `ExpressionListPanel` | Widget 리스트 관리, id 생성, id 붙여서 Signal 중계 |
| `MainWindow` | Panel/Controller 생성, Signal 연결 |
| `GraphController` | id로 GraphItem 관리 |
| `GraphItem` | 수식 파싱 + x/y 계산 |
| `GraphPanel` | id 기반 curve 관리, 렌더링 |