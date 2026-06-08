import re

# === Fix 1: start_exam 加状态检查 ===
f = open('routers/exams.py', 'r', encoding='utf-8-sig')
c = f.read()
f.close()

old = '''    exam = db.query(Exam).filter(Exam.id == eid).first()
    if not exam: raise HTTPException(status_code=404, detail="考试不存在")

    q = db.query(Question)'''

new = '''    exam = db.query(Exam).filter(Exam.id == eid).first()
    if not exam: raise HTTPException(status_code=404, detail="考试不存在")
    if exam.status != "进行中" and mode != "practice":
        raise HTTPException(status_code=400, detail="考试未开始或已结束")

    q = db.query(Question)'''

c = c.replace(old, new)
with open('routers/exams.py', 'w', encoding='utf-8') as f:
    f.write(c)
print('exams.py: added status check')

# === Fix 2: users.py update 保留 name 为空时不覆盖，密码字段修复 ===
f = open('routers/users.py', 'r', encoding='utf-8-sig')
c = f.read()
f.close()

old_func = '''@router.put("/{uid}")
def update_user(uid: int, data: UpdateUserSchema, db = Depends(get_db)):
    user = db.query(User).filter(User.id == uid).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if data.name: user.name = data.name
    if data.role: user.role = data.role
    if data.department: user.department = data.department
    if data.password: user.password_hash = hash_pw(data.password)
    db.commit()
    return {"message": "更新成功"}'''

new_func = '''@router.put("/{uid}")
def update_user(uid: int, data: UpdateUserSchema, db = Depends(get_db)):
    user = db.query(User).filter(User.id == uid).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if data.name is not None and data.name != "":
        user.name = data.name
    if data.role is not None and data.role != "":
        user.role = data.role
    if data.department is not None:
        user.department = data.department
    if data.password is not None and data.password != "":
        user.password_hash = hash_pw(data.password)
    db.commit()
    return {"message": "更新成功"}'''

c = c.replace(old_func, new_func)
with open('routers/users.py', 'w', encoding='utf-8') as f:
    f.write(c)
print('users.py: fixed update fields')

print('both fixes applied')
