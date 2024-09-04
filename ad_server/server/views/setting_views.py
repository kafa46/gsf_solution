from flask import Blueprint, render_template, request, redirect, url_for, flash


# 블루프린트 생성
bp = Blueprint('setting', __name__, url_prefix='/setting')

# 설정 페이지 라우트 (GET 요청: 페이지 렌더링, POST 요청: 설정 저장)
@bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # POST 요청 처리: 폼 데이터 가져와 설정 저장
        data = request.form.to_dict()  # 폼 데이터를 딕셔너리로 변환
        # success = save_settings(data)  # setting.py의 save_settings 함수 호출
        
        # if success:
        #     flash('Settings updated successfully!', 'success')  # 성공 메시지 플래싱
        # else:
        #     flash('Failed to update settings', 'danger')  # 실패 메시지 플래싱
        
        # return redirect(url_for('setting.index'))  # 설정 페이지로 다시 리다이렉트

    # GET 요청 처리: 설정 값 가져와 렌더링
    # settings = get_settings()  # setting.py의 get_settings 함수 호출
    return render_template('setting.html')