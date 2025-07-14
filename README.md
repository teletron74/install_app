설치확인서 앱 흐름 및 파일 역할 설명
1. '다음 페이지로 이동' 버튼 (InstallFormPage1, InstallFormPage2)
이 버튼은 현재 페이지에서 입력된 데이터를 다음 페이지로 전달하고 화면을 전환하는 역할을 합니다.

버튼 위치:

install_form_page1.dart 하단

install_form_page2.dart 하단

역할:

데이터 수집: 현재 페이지의 모든 입력 필드(텍스트, 이미지 경로, GPS 등)에서 데이터를 수집합니다.

모델 업데이트: 수집된 데이터를 InstallFormModel 객체에 저장합니다. 이 _model 객체는 앱의 모든 페이지에서 공유되는 데이터 컨테이너입니다.

화면 전환: Navigator.push()를 사용하여 다음 InstallFormPage로 이동합니다. 이때 _model 객체를 다음 페이지의 생성자(constructor)로 전달하여 데이터 연속성을 유지합니다.

관련 파일:

install_form_page1.dart, install_form_page2.dart: 버튼 UI 및 onPressed 로직 포함.

install_form_model.dart: 페이지 간에 전달되고 업데이트되는 데이터 객체.

2. 이미지 첨부 관련 버튼 (InstallFormPage2)
'카메라', '갤러리', '저장', '삭제' 버튼은 이미지와 관련된 기능을 수행합니다.

버튼 위치: install_form_page2.dart

역할:

'카메라' / '갤러리' 버튼:

권한 요청: permission_handler 패키지를 사용하여 카메라 또는 갤러리 접근 권한을 요청합니다.

이미지 선택: image_picker 패키지를 사용하여 카메라를 실행하거나 갤러리에서 이미지를 선택합니다.

모델 업데이트: 선택된 이미지의 로컬 파일 경로를 InstallFormModel의 해당 필드(예: beforeImagePath)에 저장합니다.

UI 업데이트: 선택된 이미지를 화면에 표시합니다.

'저장' 버튼:

권한 요청: 이미지 저장을 위해 저장소 접근 권한을 요청합니다.

이미지 저장: 현재 화면에 표시된 이미지를 스마트폰의 Pictures/설치확인서 폴더에 저장합니다. (이때 파일명은 기관명_이미지타입.png 형식으로 저장됩니다.)

'삭제' 버튼:

모델 업데이트: InstallFormModel의 해당 이미지 경로 필드를 null로 설정합니다.

UI 업데이트: 화면에서 이미지를 제거합니다.

관련 파일:

install_form_page2.dart: 버튼 UI 및 이미지 선택/저장/삭제 로직 포함.

install_form_model.dart: 이미지 로컬 경로를 저장.

3. 서명 관련 버튼 (InstallFormPage3)
'설치자 서명', '확인자 서명' 및 '서명 지우기' 버튼은 서명 기능을 담당합니다.

버튼 위치: install_form_page3.dart

역할:

'설치자 서명' / '확인자 서명' 버튼:

화면 전환: Navigator.push()를 사용하여 SignaturePadScreen으로 이동합니다.

서명 입력: SignaturePadScreen에서 사용자가 손가락으로 서명을 그립니다.

서명 이미지 저장: SignaturePadScreen은 그려진 서명을 이미지 파일로 변환하여 임시 로컬 경로에 저장하고, 이 경로를 install_form_page3.dart로 반환합니다.

모델 업데이트: 반환된 서명 이미지의 로컬 파일 경로를 InstallFormModel의 해당 서명 필드(예: installerSignaturePath)에 저장합니다.

UI 업데이트: install_form_page3.dart 화면에 서명 이미지를 표시합니다.

'서명 지우기' 버튼:

모델 업데이트: InstallFormModel의 해당 서명 경로 필드를 null로 설정합니다.

UI 업데이트: 화면에서 서명 이미지를 제거합니다.

'서명 저장 (갤러리)' 버튼:

권한 요청: 이미지 저장을 위해 저장소 접근 권한을 요청합니다.

서명 이미지 저장: 현재 화면에 표시된 서명 이미지를 스마트폰의 Pictures/설치확인서 폴더에 기관명_설치자.png 또는 기관명_확인자.png 형식으로 저장합니다.

관련 파일:

install_form_page3.dart: 서명 버튼 UI 및 서명 이미지 처리 로직.

signature_pad_screen.dart: 서명 그리기 UI 및 서명 이미지 파일 생성 로직.

install_form_model.dart: 서명 이미지 로컬 경로를 저장.

4. '미리보기' 버튼 (InstallFormPage3)
이 버튼은 최종 PDF가 어떻게 보일지 미리 확인하는 기능을 제공합니다.

버튼 위치: install_form_page3.dart

역할:

PDF 생성: PdfService.generateAndSavePdf 함수를 호출하여 현재 InstallFormModel의 데이터를 바탕으로 PDF 문서를 생성합니다. 이때 PDF는 아직 스마트폰에 저장되지 않고 메모리 상에만 존재합니다.

화면 전환: Navigator.push()를 사용하여 PdfPreviewScreen으로 이동합니다.

PDF 표시: PdfPreviewScreen은 printing 패키지를 사용하여 생성된 PDF를 화면에 표시합니다.

관련 파일:

install_form_page3.dart: 버튼 UI 및 미리보기 화면으로의 전환 로직.

pdf_service.dart: PDF 문서 생성 로직.

install_form_model.dart: PDF 생성에 사용되는 데이터.

pdf_preview_screen.dart: PDF 미리보기 UI.

5. '설치확인서 저장' 버튼 (InstallFormPage3)
이 버튼이 가장 중요한 부분이며, 제가 이전에 설명드린 변경 사항들이 적용되는 곳입니다. 이 버튼은 모든 데이터를 백엔드 서버로 전송하는 역할을 합니다.

버튼 위치: install_form_page3.dart

역할:

PDF 생성 및 로컬 저장:

PdfService.generateAndSavePdf 함수를 호출하여 최종 PDF 문서를 생성하고, 이를 스마트폰의 Pictures/설치확인서 폴더에 기관명_설치확인서_날짜.pdf 형식으로 저장합니다.

이 함수는 저장된 PDF 파일의 로컬 경로를 반환합니다.

백엔드 전송 준비 (MultipartRequest):

http 패키지의 MultipartRequest 객체를 생성합니다. 이 객체는 텍스트 데이터와 파일 데이터를 동시에 보낼 수 있는 특별한 HTTP 요청 방식입니다.

텍스트 데이터 추가: InstallFormModel의 모든 텍스트 필드(기관명, 사업명, 설치자 이름, GPS 위도/경도 등)를 request.fields에 일반 폼 데이터 형태로 추가합니다.

파일 데이터 추가:

InstallFormModel에 저장된 모든 이미지 파일(설치 전/후, VPN, 라우터, 설치자/확인자 서명)의 로컬 경로를 사용하여 http.MultipartFile.fromPath()를 호출합니다.

이 함수는 로컬 경로의 파일을 읽어 MultipartRequest에 첨부할 수 있는 형태로 변환합니다.

마찬가지로, 1단계에서 생성된 PDF 파일의 로컬 경로를 사용하여 PDF 파일도 MultipartFile 형태로 첨부합니다.

이때 백엔드에서 파일을 구분할 수 있도록 각 파일에 고유한 필드 이름(예: beforeImage, installationPdf)을 부여합니다.

백엔드 전송: 준비된 MultipartRequest를 백엔드 서버로 전송합니다.

응답 처리:

서버로부터 응답을 받습니다.

응답 코드가 200 또는 201(성공)이면, 데이터가 성공적으로 저장되었음을 사용자에게 알리고 앱의 첫 페이지로 돌아갑니다.

응답 코드가 실패를 나타내면, 오류 메시지를 사용자에게 표시합니다.

관련 파일:

install_form_page3.dart: 버튼 UI 및 백엔드 전송 로직의 핵심.

pdf_service.dart: PDF 생성 및 로컬 저장 로직.

install_form_model.dart: 백엔드로 전송될 모든 데이터 (텍스트 및 파일 경로).

http 패키지: 실제 HTTP 요청을 처리.

데이터 흐름 요약
페이지 1, 2, 3: 사용자가 데이터를 입력하고 이미지를 첨부하며 서명합니다. 이 모든 데이터는 InstallFormModel 객체에 로컬 파일 경로 형태로 저장됩니다.

'설치확인서 저장' 버튼 클릭:

pdf_service.dart가 InstallFormModel의 데이터를 사용하여 PDF를 생성하고 로컬에 저장한 후, 그 로컬 경로를 install_form_page3.dart로 반환합니다.

install_form_page3.dart는 http.MultipartRequest를 사용하여 InstallFormModel의 텍스트 데이터와, 모델에 저장된 모든 로컬 이미지/PDF 파일 경로를 읽어 실제 파일 데이터를 백엔드로 전송합니다.

백엔드:

MultipartRequest를 받아 텍스트 데이터를 DB에 저장하고, 첨부된 파일들을 서버의 \static\uploads\ 폴더에 저장합니다.

DB에는 저장된 파일들의 서버 경로(\static\uploads\기관명_이미지타입.png 등)를 기록합니다.

이러한 방식으로, 앱은 로컬 파일 경로를 관리하고, 최종적으로 '설치확인서 저장' 버튼을 통해 필요한 파일들을 백엔드로 업로드하며, DB에는 해당 파일들의 서버 상의 경로를 저장하게 됩니다.
