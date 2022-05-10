def set_text(session_id):
    with open('inputs/session.txt', "w") as myfile:
        myfile.write(str(session_id))


def get_text():
    with open(r'/allen/programs/mindscope/workgroups/openscope/ahad/test_cron/OpenScopeNWB-feature-firebase_testing/scripts/deciphering_variability/inputs/session.txt', "r") as myfile:
        lines = myfile.read()
    return lines
