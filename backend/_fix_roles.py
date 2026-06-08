# === Step 1: 更新数据库: admin -> super_admin ===
import sqlite3
c = sqlite3.connect('exam.db')
c.execute("UPDATE users SET role='super_admin' WHERE id=1 AND role='admin'")
c.commit()
r = c.execute("SELECT id, username, role FROM users").fetchall()
for row in r:
    print(f'  {row[0]}: {row[1]} ({row[2]})')
c.close()
print('database updated')

# === Step 2: 后端 users.py 增加权限控制 ===
f = open('routers/users.py', 'r', encoding='utf-8-sig')
content = f.read()
f.close()
content = content.lstrip('\ufeff')

# 加 require_super_admin 函数
# 在 hash_pw 函数后面添加
old_func_end = 'def hash_pw(pw):\n    salt = secrets.token_hex(16)\n    h = hashlib.sha256((salt + pw).encode()).hexdigest()\n    return salt + ":" + h\n\n'
new_func_end = old_func_end + '''def require_super_admin(user = Depends(get_current_user)):
    if user.role != "super_admin":
        raise HTTPException(status_code=403, detail="需要超级管理员权限")
    return user

def require_super_or_admin(user = Depends(get_current_user)):
    if user.role not in ("super_admin", "admin"):
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return user

'''
content = content.replace(old_func_end, new_func_end)

# 修改 create_user: require_super_or_admin
old_create = '''@router.post("")
def create_user(data: CreateUserSchema, db = Depends(get_db)):'''
new_create = '''@router.post("")
def create_user(data: CreateUserSchema, user = Depends(require_super_or_admin), db = Depends(get_db)):'''
content = content.replace(old_create, new_create)

# 修改 update_user: super_admin 可以改任何用户，admin 只能改考生
old_update = '''@router.put("/{uid}")
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

new_update = '''@router.put("/{uid}")
def update_user(uid: int, data: UpdateUserSchema, current_user = Depends(get_current_user), db = Depends(get_db)):
    target = db.query(User).filter(User.id == uid).first()
    if not target:
        raise HTTPException(status_code=404, detail="用户不存在")
    if current_user.role == "admin" and target.role != "candidate":
        raise HTTPException(status_code=403, detail="普通管理员只能修改考生信息")
    if data.name is not None and data.name != "":
        target.name = data.name
    if data.role is not None and data.role != "":
        if current_user.role == "super_admin":
            target.role = data.role
        elif current_user.role == "admin" and target.role == "candidate":
            # admin 不能提升自己到 super_admin
            if data.role != "super_admin":
                target.role = data.role
    if data.department is not None:
        target.department = data.department
    if data.password is not None and data.password != "":
        target.password_hash = hash_pw(data.password)
    db.commit()
    return {"message": "更新成功"}'''

content = content.replace(old_update, new_update)

# 修改 delete_user
old_delete = '''@router.delete("/{uid}")
def delete_user(uid: int, db = Depends(get_db)):
    user = db.query(User).filter(User.id == uid).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if user.role == "admin":
        raise HTTPException(status_code=400, detail="不能删除管理员")'''

new_delete = '''@router.delete("/{uid}")
def delete_user(uid: int, current_user = Depends(get_current_user), db = Depends(get_db)):
    target = db.query(User).filter(User.id == uid).first()
    if not target:
        raise HTTPException(status_code=404, detail="用户不存在")
    if current_user.role != "super_admin":
        raise HTTPException(status_code=403, detail="只有超级管理员才能删除用户")
    if target.role == "super_admin":
        raise HTTPException(status_code=400, detail="不能删除超级管理员")'''

content = content.replace(old_delete, new_delete)

# 修改 list_users: 不需要权限（查看列表所有人）
old_list = '''@router.get("")
def list_users(db = Depends(get_db)):
    users = db.query(User).order_by(User.id.desc()).all()'''
new_list = '''@router.get("")
def list_users(user = Depends(get_current_user), db = Depends(get_db)):
    users = db.query(User).order_by(User.id.desc()).all()'''
content = content.replace(old_list, new_list)

with open('routers/users.py', 'w', encoding='utf-8') as f:
    f.write('\ufeff' + content)
print('users.py updated')

# === Step 3: 后端 auth.py login 返回 role 字段已存在 ===
# 不需要改
print('all backend changes done')
