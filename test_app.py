import pytest
from app import app, inventory, user_balance  # 假设app.py是主模块，导入app和模拟数据

# 重置模拟数据以确保每个测试独立
@pytest.fixture(autouse=True)
def reset_data():
    inventory["book"] = 10
    user_balance["default_user"] = 100

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_order_success(client):
    """测试正常下单：库存和支付成功"""
    response = client.post('/order', json={"item": "book", "qty": 2, "user_id": "default_user"})
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True
    assert data['剩余库存'] == 8
    assert data['支付金额'] == 20
    assert data['剩余余额'] == 80

def test_order_inventory_insufficient(client):
    """测试库存不足：触发ValueError"""
    # 先扣减到只剩1本
    inventory["book"] = 1
    response = client.post('/order', json={"item": "book", "qty": 2})
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    assert data['error'] == "库存不足"

def test_order_balance_insufficient(client):
    """测试余额不足：触发ValueError"""
    # 设置余额只够1本
    user_balance["default_user"] = 10
    response = client.post('/order', json={"item": "book", "qty": 2})
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    assert data['error'] == "余额不足"

def test_order_item_not_exist(client):
    """测试商品不存在：触发ValueError"""
    response = client.post('/order', json={"item": "nonexistent", "qty": 1})
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    assert data['error'] == "不存在的商品"

def test_order_invalid_qty(client):
    """测试无效qty：参数校验失败"""
    response = client.post('/order', json={"item": "book", "qty": 0})
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    assert data['error'] == "qty 必须是正整数"

def test_order_missing_item(client):
    """测试缺少item：参数校验失败"""
    response = client.post('/order', json={"qty": 1})
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    assert data['error'] == "缺少商品名"

def test_order_boundary_max_qty(client):
    """测试边界：正好扣完库存"""
    response = client.post('/order', json={"item": "book", "qty": 10})
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True
    assert data['剩余库存'] == 0
    assert data['剩余余额'] == 0  # 正好100元扣完

def test_order_user_not_exist(client):
    """测试用户不存在：触发ValueError"""
    response = client.post('/order', json={"item": "book", "qty": 1, "user_id": "unknown"})
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    assert data['error'] == "用户不存在"

def test_order_non_integer_qty(client):
    """测试qty非整数：参数校验（但JSON中qty如果是字符串，会被get作为str，但代码中检查isinstance(int)）"""
    response = client.post('/order', json={"item": "book", "qty": "two"})
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    assert data['error'] == "qty 必须是正整数"