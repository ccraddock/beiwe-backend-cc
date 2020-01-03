#script: reset staging with some live data

for study in Studies():
    if study.name !="Debugging Study":
        study.remove()

for admin in Admins():
    if admin._id not in ['eli', "josh"]:
        admin.remove()

Admin("eli").set_password("1")
Admin("josh").set_password("1")

debug_id = Study(name="Debugging Study")._id
safe_users = set(Users(study_id=debug_id, field="_id"))

for user in Users():
    if user._id not in safe_users:
        user.remove()

FileToProcess.db().drop()

i=0
for chunk in ChunksRegistry.iterator():
    i += 1
    if i % 1000 == 0:
        print i
    if chunk.user_id not in safe_users:
        chunk.remove()
