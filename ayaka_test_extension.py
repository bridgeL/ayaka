from ayaka_test import fake_cq


@fake_cq.on_api("get_group_member_info")
async def get_group_member_info(echo: int, params: dict):
    await fake_cq.send_echo(echo, {"user_id": params["user_id"], "card": params["user_id"]})
