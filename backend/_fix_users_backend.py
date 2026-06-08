f = open('routers/users.py', 'r', encoding='utf-8-sig')
c = f.read()
f.close()
c = c.lstrip('\ufeff')

# 导入 get_current_user
c = c.replace('from models import User\nimport hashlib, secrets', 'from models import User\nfrom .auth import get_current_user\nimport hashlib, secrets')

# 修改 list_users: 需要登录
c = c.replace('def list_users(db = Depends(get_db)):', 'def list_users(user = Depends(get_current_user), db = Depends(get_db)):')

# 修改 create_user: 需要 admin 或 super_admin
c = c.replace('def create_user(data: CreateUserSchema, db = Depends(get_db)):', 'def create_user(data: CreateUserSchema, user = Depends(get_current_user), db = Depends(get_db)):\n    if user.role not in (\"admin\", \"super_admin\"):\n        raise HTTPException(status_code=403, detail=\"需要管理员权限\")')

# 修改 update_user: 权限控制
old_update = '''@router.put(\"/{uid}\")
def update_user(uid: int, data: UpdateUserSchema, db = Depends(get_db)):
    user = db.query(User).filter(User.id == uid).first()
    if not user:
        raise HTTPException(status_code=404, detail=\"用户不存在\")
    if data.name: user.name = data.name
    if data.role: user.role = data.role
    if data.department: user.department = data.department
    if data.password: user.password_hash = hash_pw(data.password)
    db.commit()
    return {\"message\": \"更新成功\"}'''

new_update = '''@router.put(\"/{uid}\")
def update_user(uid: int, data: UpdateUserSchema, current_user = Depends(get_current_user), db = Depends(get_db)):
    target = db.query(User).filter(User.id == uid).first()
    if not target:
        raise HTTPException(status_code=404, detail=\"用户不存在\")
    if current_user.role == \"super_admin\":
        pass  # super_admin can edit anyone
    elif current_user.role == \"admin\" and target.role == \"candidate\" and data.role in (None, \"\", \"candidate\"):
        pass  # admin can edit candidates, but cannot change their role to admin
    elif current_user.role == \"admin\" and target.role == \"candidate\":
        pass  # admin can edit candidates
    else:
        raise HTTPException(status_code=403, detail=\"权限不足\")
    if data.name: target.name = data.name
    if data.role: target.role = data.role
    if data.department: target.department = data.department
    if data.password: target.password_hash = hash_pw(data.password)
    db.commit()
    return {\"message\": \"更新成功\"}'''

c = c.replace(old_update, new_update)

# 修改 delete_user
old_delete = '''@router.delete(\"/{uid}\")
def delete_user(uid: int, db = Depends(get_db)):
    user = db.query(User).filter(User.id == uid).first()
    if not user:
        raise HTTPException(status_code=404, detail=\"用户不存在\")
    if user.role == \"admin\":
        raise HTTPException(status_code=400, detail=\"不能删除管理员\")
    db.delete(user)
    db.commit()
    return {\"message\": \"删除成功\"}'''

new_delete = '''@router.delete(\"/{uid}\")
def delete_user(uid: int, current_user = Depends(get_current_user), db = Depends(get_db)):
    target = db.query(User).filter(User.id == uid).first()
    if not target:
        raise HTTPException(status_code=404, detail=\"用户不存在\")
    if current_user.role != \"super_admin\":
        raise HTTPException(status_code=403, detail=\"只有超级管理员可以删除用户\")
    if target.role == \"super_admin\":
        raise HTTPException(status_code=400, detail=\"不能删除超级管理员\")
    db.delete(target)
    db.commit()
    return {\"message\": \"删除成功\"}'''

c = c.replace(old_delete, new_delete)

with open('routers/users.py', 'w', encoding='utf-8') as f:
    f.write('\ufeff' + c)

print('users.py updated')
