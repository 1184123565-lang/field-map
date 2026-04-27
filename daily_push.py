#!/usr/bin/env python3
"""
每日晨间推送 - 小鹿中医陌拜地图
每天早上推送今日待办、晚间电话队列到微信
"""

import json, urllib.request, urllib.parse
from datetime import datetime, timedelta

# ===== 配置 =====
SENDKEY = "SCT342236ThK5t2r9Wj9mT6m1LFw3GsgOi"
DATA_FILE = "/Users/pl1688/WorkBuddy/20260425092842/field-map/records.json"

# ===== 读取数据 =====
def load_records():
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# ===== 数据分析 =====
def analyze(records):
    today = datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

    today_records = [r for r in records if str(r.get('createdAt', '')).startswith(today)]
    yesterday_records = [r for r in records if str(r.get('createdAt', '')).startswith(yesterday)]

    # 今晚电话队列：有电话 + 近期 + 有意向/待跟进 + 未拨打
    call_queue = [
        r for r in records
        if r.get('phone') and str(r['phone']).strip()
        and str(r.get('createdAt', '')) >= week_ago
        and r.get('callStatus') != 'done'
        and any(k in str(r.get('result', '')) for k in ['有意向', '待跟进'])
    ]
    call_queue.sort(key=lambda r: (
        {'high': 0, 'normal': 1, 'low': 2}.get(r.get('priority', 'normal'), 1),
        -datetime.fromisoformat(r['createdAt']).timestamp()
    ))

    # 有意向客户
    interested = [r for r in records if any(k in str(r.get('result', '')) for k in ['有意向', '待跟进'])]
    urgent = [r for r in interested if r.get('priority') == 'high']

    # 本周趋势
    week_days = {}
    for i in range(7):
        d = datetime.now() - timedelta(days=i)
        day_str = d.strftime('%Y-%m-%d')
        week_days[day_str] = len([r for r in records if str(r.get('createdAt', '')).startswith(day_str)])

    return {
        'today': today,
        'today_count': len(today_records),
        'yesterday_count': len(yesterday_records),
        'total': len(records),
        'call_queue': call_queue[:8],
        'interested': interested,
        'urgent': urgent[:5],
        'week_days': week_days
    }

# ===== 构建消息 =====
WEEKDAY = ['周一','周二','周三','周四','周五','周六','周日']

def mask_phone(phone):
    s = str(phone).strip()
    if len(s) >= 7:
        return s[:3] + '****' + s[-4:]
    return s

def build_message(data):
    now = datetime.now()
    date_str = now.strftime('%m月%d日')
    weekday = WEEKDAY[now.weekday()]
    today_str = f"{date_str} {weekday}"

    lines = []
    title = f"📋 今日陌拜提醒 | {today_str}"

    # 今日概况
    lines.append("【今日概况】")
    lines.append(f"  今日新增：{data['today_count']} 家  昨日：{data['yesterday_count']} 家")
    lines.append(f"  累计收录：{data['total']} 家")
    lines.append("")

    # 晚间电话队列
    queue = data['call_queue']
    if queue:
        lines.append(f"【📞 今晚电话队列】共 {len(queue)} 人（按优先级排序）")
        for i, r in enumerate(queue, 1):
            tag = '⭐' if '有意向' in str(r.get('result', '')) else '📅'
            fire = '🔥' if r.get('priority') == 'high' else '  '
            name = str(r.get('name', '未知诊所'))
            phone = mask_phone(r.get('phone', ''))
            note = str(r.get('note', ''))
            lines.append(f"  {fire}{i}. {name} {tag}")
            lines.append(f"      📱 {phone}" + (f"  备注: {note}" if note else ""))
        lines.append("")
    else:
        lines.append("【📞 今晚电话】暂无待电客户，建议扫附近开发新资源")
        lines.append("")

    # 重点跟进
    urgent = data['urgent']
    interested = data['interested']
    if urgent:
        lines.append(f"【🔥 重点跟进】{len(urgent)} 家")
        for r in urgent:
            name = str(r.get('name', '未知'))
            phone = mask_phone(r.get('phone', ''))
            result = str(r.get('result', '')).replace('已拜访-', '')
            lines.append(f"  · {name} {result}")
            lines.append(f"    {phone}")
        lines.append("")
    elif interested:
        lines.append(f"【⭐ 意向客户】共 {len(interested)} 家待跟进")
        for r in interested[:3]:
            lines.append(f"  · {r.get('name','未知')}  {mask_phone(r.get('phone',''))}")
        lines.append("")

    # 行动建议
    lines.append("【💡 今日行动建议】")
    if data['today_count'] == 0:
        lines.append("  今日还未开始收录，建议先「扫附近」开发新资源")
    elif len(queue) == 0:
        lines.append("  今晚暂无待电客户，今天多跑几家补充电话队列")
    if data['urgent']:
        lines.append(f"  优先联系 {urgent[0].get('name','首位')}，标记为紧急跟进")
    lines.append("")

    lines.append("【📱 工具入口】")
    lines.append("  陌拜地图：http://localhost:7823")

    return title, '\n'.join(lines)

# ===== 发送微信 =====
def send_wechat(title, content):
    url = f"https://sctapi.ftqq.com/{SENDKEY}.send"
    payload = json.dumps({
        "title": title,
        "desp": content
    }).encode('utf-8')

    req = urllib.request.Request(url, data=payload, headers={
        "Content-Type": "application/json"
    }, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            if result.get('code') == 0:
                print(f"✅ 推送成功！")
                return True
            else:
                print(f"❌ 推送失败: {result}")
                return False
    except Exception as e:
        print(f"❌ 推送异常: {e}")
        return False

# ===== 主程序 =====
if __name__ == "__main__":
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"\n{'='*40}")
    print(f"🕗 [{now_str}] 小鹿中医 · 每日晨间推送")
    print(f"{'='*40}\n")

    records = load_records()
    print(f"📊 读取到 {len(records)} 条记录")

    if not records:
        print("⚠️ 暂无数据，请先在陌拜地图中收录诊所")
        print("💡 推送跳过，等待下次执行")
    else:
        data = analyze(records)
        title, content = build_message(data)

        print(f"\n📋 推送内容预览:")
        print("-" * 36)
        print(content)
        print("-" * 36)

        send_wechat(title, content)

    print()
