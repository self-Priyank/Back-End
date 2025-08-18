total_status = ["complete", "delaycomplete", "pending", "overdue", "archived"]
def is_invalid_status(sv):
    if sv not in total_status:
        return True
    return False

def process_data(d):
    d["id"] = str(d["_id"])
    del d["_id"]
    return d