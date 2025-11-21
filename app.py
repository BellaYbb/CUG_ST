from flask import Flask, request, jsonify

app = Flask(__name__)

# 模拟库存模块
inventory = {"book": 10}

def check_and_update_inventory(item, qty):
    """库存模块：检查并扣减库存"""
    if item not in inventory:
        raise ValueError("不存在的商品")
    if inventory[item] < qty:
        raise ValueError("库存不足")
    inventory[item] -= qty
    return inventory[item]

# 模拟支付模块（假设用户有固定余额）
user_balance = {"default_user": 100}  # 假设每本书10元

def process_payment(item, qty, user_id="default_user"):
    """支付模块：模拟扣款"""
    price_per_item = 10  # 固定价格
    total_cost = price_per_item * qty
    if user_id not in user_balance:
        raise ValueError("用户不存在")
    if user_balance[user_id] < total_cost:
        raise ValueError("余额不足")
    user_balance[user_id] -= total_cost
    return total_cost, user_balance[user_id]

# 下单模块（整合库存和支付）
@app.route("/order", methods=["POST"])
def order():
    """
    下单接口
    请求体 JSON: {"item": "book", "qty": 2, "user_id": "default_user"}
    """
    data = request.get_json(force=True, silent=True) or {}
    item = data.get("item")
    qty = data.get("qty", 1)
    user_id = data.get("user_id", "default_user")

    # 参数校验
    if not item or not isinstance(item, str):
        return jsonify({"error": "缺少商品名"}), 400
    if not isinstance(qty, int) or qty <= 0:
        return jsonify({"error": "qty 必须是正整数"}), 400

    try:
        # 库存模块调用
        remaining_inventory = check_and_update_inventory(item, qty)
        
        # 支付模块调用
        total_cost, remaining_balance = process_payment(item, qty, user_id)
        
        return jsonify({
            "success": True,
            "剩余库存": remaining_inventory,
            "支付金额": total_cost,
            "剩余余额": remaining_balance
        })
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True)