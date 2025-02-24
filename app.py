# from flask import Flask, render_template, request, jsonify
# from dotenv import load_dotenv

# load_dotenv()

# from ice_breaker import ice_break_with


# app = Flask(__name__)


# @app.route("/")
# def index():
#     return render_template("index.html")


# @app.route("/process", methods=["POST"])
# def process():
#     name = request.form["name"]
#     summary_and_facts, interests, ice_breakers, profile_pic_url = ice_break_with(
#         name=name
#     )
#     return jsonify(
#         {
#             "summary_and_facts": summary_and_facts.to_dict(),
#             "interests": interests.to_dict(),
#             "ice_breakers": ice_breakers.to_dict(),
#             "picture_url": profile_pic_url,
#         }
#     )


# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5001, debug=True)


from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
load_dotenv()

# 위에서 작성한 함수 import
from ice_breaker import ice_break_with

app = Flask(__name__)

@app.route("/")
def index():
    # index.html 렌더링
    return render_template("index.html")

@app.route("/process", methods=["POST"])
def process():
    name = request.form["name"]

    # ice_break_with 로부터 4개 값 받기
    summary_and_facts, interests, ice_breakers, profile_pic_url = ice_break_with(name)

    # Flask -> JSON 응답
    return jsonify(
        {
            "summary_and_facts": summary_and_facts.to_dict(),  # {"summary": "...", "facts": [...]}
            "interests": interests.to_dict(),                  # {"topics_of_interest": [...]}
            "ice_breakers": ice_breakers.to_dict(),            # {"ice_breakers": [...]}
            "picture_url": profile_pic_url,
        }
    )

if __name__ == "__main__":
    # 다른 곳에서 이미 5000을 쓰고 있다면 port=5001
    app.run(host="0.0.0.0", port=5001, debug=True)
