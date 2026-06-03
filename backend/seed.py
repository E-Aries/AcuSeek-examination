import hashlib, secrets
from database import SessionLocal, engine, Base
from models import User, Question

Base.metadata.create_all(bind=engine)

def hash_pw(pw):
    salt = secrets.token_hex(16)
    h = hashlib.sha256((salt + pw).encode()).hexdigest()
    return salt + ":" + h

def verify_pw(pw, stored):
    salt, h = stored.split(":")
    return hashlib.sha256((salt + pw).encode()).hexdigest() == h

db = SessionLocal()
try:
    if not db.query(User).first():
        db.add(User(username="admin", password_hash=hash_pw("admin123"), name="管理员", role="admin"))
        db.add(User(username="zhangsan", password_hash=hash_pw("123456"), name="张明", role="candidate", department="售后一部"))
        db.add(User(username="lisi", password_hash=hash_pw("123456"), name="李华", role="candidate", department="售后二部"))
        print("Users created!")

    if not db.query(Question).first():
        qs = [
            Question(type="单选", category="售后流程", content="客户保修期外要求免费维修，以下哪种处理方式最合适？", options=[{"label":"A","text":"直接拒绝"},{"label":"B","text":"解释保修政策并提供付费维修"},{"label":"C","text":"先修再补"},{"label":"D","text":"转交他人"}], answer="B", difficulty=2, score=2),
            Question(type="多选", category="产品知识", content="以下哪些属于核心功能模块？", options=[{"label":"A","text":"用户管理"},{"label":"B","text":"数据报表"},{"label":"C","text":"邮件发送"},{"label":"D","text":"权限控制"}], answer='["A","D"]', difficulty=2, score=3),
            Question(type="判断", category="故障处理", content="设备红灯闪烁表示正常运行。", options=[{"label":"正确","text":""},{"label":"错误","text":""}], answer="错误", difficulty=1, score=1),
            Question(type="填空", category="售后流程", content="客户投诉应在 ____ 小时内响应。", answer="24", difficulty=2, score=2),
            Question(type="简答", category="故障处理", content="简述设备无法开机的排查步骤。", difficulty=3, score=5),
            Question(type="单选", category="产品知识", content="XX 产品的标准保修期限是？", options=[{"label":"A","text":"1年"},{"label":"B","text":"2年"},{"label":"C","text":"3年"},{"label":"D","text":"5年"}], answer="C", difficulty=1, score=2),
        ]
        for q in qs: db.add(q)
        print("Questions created!")
    db.commit()
    print("Seed data created successfully!")
finally:
    db.close()
