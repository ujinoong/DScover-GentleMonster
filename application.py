from flask import Flask, render_template, request, redirect, url_for
import sys
from face_shape import get_faceshape
from glasses2 import get_glass_img
import uuid


application = Flask(__name__)


@application.route("/")  # 기본 페이지 설정하기
def hello():
    return render_template('index.html')


# 남/여 별로 모든 item 이름 list
male_all_item = ['리버티', '에디', '알리오', '탭탭', '차차', '우나씨', 'S.O.A', '루토', '다디오', '다니오', '데이', '넵']
female_all_item = ['사우스사이드', '밀란 A C2', '키토 1', '제니 - 클라우디 데이 온리', '디어 클래식 X 02', '죠죠', '제프', '디온', '만투', '죠죠', '키토 2']

# # 딕셔너리에 이름 별로 위치 저장해주기
# male_item_loc ={'리버티':'static/glass_item_img/남자_각진_1.jpg', '에디':'static/glass_item_img/남자_각진_2.jpg', '알리오':'static/glass_item_img/남자_각진_3.jpg',
# '탭탭':'static/glass_item_img/남자_긴_1.jpg', '차차':'static/glass_item_img/남자_긴_2.jpg', '우나씨':'static/glass_item_img/남자_긴_3.jpg',
# 'S.O.A':'static/glass_item_img/남자_둥근_1.jpg', '루토':'static/glass_item_img/남자_둥근_2.jpg', '다니오':'static/glass_item_img/남자_둥근_3.jpg',
# '다니오':'static/glass_item_img/남자_역삼각형_1.jpg', '데이':'static/glass_item_img/남자_역삼각형_2.jpg', '넵':'static/glass_item_img/남자_역삼각형_3.jpg'}
# female_item_loc = {'사우스사이드':'static/glass_item_img/여자_둥근_1.jpg', '밀란 A C2':'static/glass_item_img/여자_둥근_2.jpg', '키토 1':'static/glass_item_img/여자_둥근_3.jpg',
# '제니 - 클라우디 데이 온리':'static/glass_item_img/여자_각진_1.jpg', '디어 클래식 X 02':'static/glass_item_img/여자_각진_2.jpg', '죠죠':'static/glass_item_img/여자_각진_3.jpg',
# '제프':'static/glass_item_img/여자_긴_1.jpg', '디온':'static/glass_item_img/여자_긴_2.jpg', '만투':'static/glass_item_img/여자_긴_3.jpg',
# '죠죠':'static/glass_item_img/여자_역삼각형_1.jpg', '키토 2':'static/glass_item_img/여자_역삼각형_2.jpg'}


def get_reco(gender, faceshape):
    if gender == 'male':
        if faceshape == '각진 얼굴형':
            return male_all_item[:3]
        elif faceshape == '긴 얼굴형':
            return male_all_item[3:6]
        elif faceshape == '둥근 얼굴형':
            return male_all_item[6:9]
        elif faceshape == '역삼각 얼굴형':
            return male_all_item[9:]
        elif faceshape == '계란 얼굴형':
            return ['무엇이든 잘 어울립니다!!']
        else:
            return['얼굴을 인식하지 못했습니다.']
    elif gender == 'female':
        if faceshape == '둥근 얼굴형':
            return female_all_item[:3]
        elif faceshape == '각진 얼굴형':
            return female_all_item[3:6]
        elif faceshape == '긴 얼굴형':
            return female_all_item[6:9]
        elif faceshape == '역삼각 얼굴형':
            return female_all_item[9:]
        elif faceshape == '계란 얼굴형':
            return ['무엇이든 잘 어울립니다!!']
        else:
            return['얼굴을 인식하지 못했습니다.']


@application.route("/uploaded/", methods=['GET', 'POST'])
def upload_done():
    if request.method == 'POST':
        uploaded_files = request.files['file']    
        # 파일명 겹치는 것 방지하기 위해 UUID 사용하여 저장
        global filename
        filename = uuid.uuid4().__str__()
        uploaded_files.save('static/img/{}.jpg'.format(filename))

        # 저장된 위치 변수 만들어주기
        global person_pic_loc
        person_pic_loc = 'static/img/{}.jpg'.format(filename)

        # 얼굴형 구하는 함수로 얼굴형 구하기
        global faceshape
        faceshape = get_faceshape(person_pic_loc)
        if faceshape == "2명 이상" or faceshape == "얼굴 X":
            return render_template('index1.html', result="사진에 얼굴이 인식되지 않았거나, 2명 이상이 인식되었습니다. 다른 사진을 업로드 해주세요.")
        
        # Input(radio)로 받은 값 저장하기
        global gender
        gender = request.form['gender']
        global html_file
        if gender == 'male':
            html_file = 'result_male.html'
        else:
            html_file = 'result_female.html'

        global male_all_item
        global female_all_item
            # get_reco 함수  사용해서 추천하는 아이템 리스트 가져오기
        global suggesting_items
        suggesting_items = get_reco(gender, faceshape)

        global all_item
        if gender == 'male':
            all_item = list(set(male_all_item))
        elif gender == 'female':
            all_item = list(set(female_all_item))



        return render_template(html_file, result='img/{}.jpg'.format(filename), faceshape=faceshape, gender=gender, sug = suggesting_items, all_item = all_item)

    elif request.method =='GET':
        return render_template('index.html')


@application.route("/glasses/", methods=['POST', 'GET'])
def reload():
    global gender
    if gender == 'male':
        glass = 'static/glassimg/male/'+request.form['selection']
    else:
        glass = 'static/glassimg/female/'+request.form['selection']
    glass_filename = uuid.uuid4().__str__()
    get_glass_img(person_pic_loc, glass, glass_filename)
    
    
    return render_template(html_file, result='result/{}.jpg'.format(glass_filename), glass=glass, faceshape=faceshape, sug = suggesting_items, all_item = all_item, test='glass_item_img/angled1.jpg')

#render_template('result.html', result='img/0.jpg', faceshape=faceshape, sug = suggesting_items, sug_x = suggesting_x_items, left_over=left_over, gender=gender, test='glass_item_img/남자_각진_1.jpg')



if __name__ == "__main__":
    application.run(host='0.0.0.0', debug=True)