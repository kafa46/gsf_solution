import os
import numpy as np
from flask import Blueprint, jsonify, render_template, request
from PIL import Image
from flask_socketio import emit
from server import dra
from server import socketio
from config import ARGS

bp = Blueprint('main', __name__, url_prefix='/')

@bp.route('/')
def index():
    return render_template(
        "index.html"
    )


@bp.route('/monitor/', methods=['GET', 'POST'])
def monitor():
    if request.method == 'POST':
        uploaded_file = request.files.get('image')
        classname = request.form.get('classname')
        
        print('--------------'*5)
        # print(f'filename: {uploaded_file.filename}')
        label = False if classname=='good' else True
        print(f'uploaded_file.filename: {uploaded_file.filename}')
        print(f'classname: {classname}')
        img = Image.open(uploaded_file).convert('RGB')
        # img.save(os.path.join('saved_imgs', ))
        anomaly_info = dra.inference(img)
        anomaly_info['label'] = label
        print(f'Anomaly: {anomaly_info}')
        socketio.emit('anomaly_status', anomaly_info)
        
    return render_template(
        'monitor.html',
        threshlod=dra.threshold,
    )

@bp.route('/threshold/', methods=['POST'])
def threshlod():
    '''탐지 Threshlod 변경'''
    sensitivity = request.form['sensitivity']
    print(sensitivity)
    
    if sensitivity == 'high':
        dra.threshold = ARGS['z-score_threshold-high']
    elif sensitivity == 'middle':
        dra.threshold = ARGS['z-score_threshold-middle']
    elif sensitivity == 'low':
        dra.threshold = ARGS['z-score_threshold-low']
    print(f'dra.threshold: {dra.threshold}')
    
    return jsonify({
        'status': 'success',
        'sensitivity': sensitivity,
        'threshold': dra.threshold
    })
    
@bp.route('/setting/')
def setting():
    return render_template(
        'setting.html'
    )