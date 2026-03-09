#!/usr/bin/env python3
"""
TeleStats - Telegram Dashboard Generator
https://github.com/thechariith/telestats
"""

from telethon import TelegramClient
from telethon.tl.types import Channel, Chat, User
from datetime import datetime
import webbrowser
import os
import sys

def get_credentials():
    """Get API credentials from environment or prompt user"""
    
    api_id = os.environ.get('TG_API_ID')
    api_hash = os.environ.get('TG_API_HASH')
    
    if api_id and api_hash:
        return int(api_id), api_hash
    
    print("\n" + "="*60)
    print("⚡ TeleStats - Telegram Dashboard Generator")
    print("="*60)
    print("\n📝 First time setup - You need Telegram API credentials\n")
    print("Follow these steps:")
    print("  1. Visit: https://my.telegram.org")
    print("  2. Log in with your phone number")
    print("  3. Go to 'API Development Tools'")
    print("  4. Create a new application (any name works)")
    print("  5. Copy your credentials below\n")
    print("-"*60)
    
    try:
        api_id_input = input("\n📱 Enter API ID: ").strip()
        api_hash_input = input("🔑 Enter API Hash: ").strip()
        
        if not api_id_input or not api_hash_input:
            print("\n❌ Error: Both API ID and Hash are required!")
            sys.exit(1)
        
        try:
            api_id = int(api_id_input)
        except ValueError:
            print("\n❌ Error: API ID must be a number!")
            sys.exit(1)
        
        return api_id, api_hash_input
        
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

api_id, api_hash = get_credentials()
client = TelegramClient('telestats_session', api_id, api_hash)

async def generate_dashboard():
    await client.start()
    
    me = await client.get_me()
    print(f"\n✅ Logged in as: {me.first_name}")
    print("📊 Fetching data...\n")
    
    dialogs = await client.get_dialogs()
    
    channels, groups, private_chats, bots = [], [], [], []
    
    for dialog in dialogs:
        entity = dialog.entity
        username = getattr(entity, 'username', None)
        
        if username:
            link = f"https://t.me/{username}"
        elif isinstance(entity, User):
            link = f"tg://user?id={entity.id}"
        else:
            link = f"tg://resolve?domain={entity.id}"
        
        chat_data = {
            "name": dialog.name or "Unknown",
            "id": dialog.id,
            "unread": dialog.unread_count,
            "link": link,
            "username": username or ""
        }
        
        if isinstance(entity, Channel):
            (channels if entity.broadcast else groups).append(chat_data)
        elif isinstance(entity, Chat):
            groups.append(chat_data)
        elif isinstance(entity, User):
            (bots if entity.bot else private_chats).append(chat_data)
    
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TeleStats - Telegram Dashboard</title>
    <meta name="description" content="Your personal Telegram dashboard">
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>📊</text></svg>">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: #fafafa;
            color: #1a1a1a;
            min-height: 100vh;
        }}
        
        .app {{
            display: grid;
            grid-template-columns: 240px 1fr;
            min-height: 100vh;
        }}
        
        .sidebar {{
            background: #fff;
            border-right: 1px solid #eee;
            padding: 32px 0;
            position: sticky;
            top: 0;
            height: 100vh;
        }}
        
        .logo {{
            padding: 0 24px 32px;
            font-size: 1.1rem;
            font-weight: 700;
            letter-spacing: -0.3px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .logo-icon {{
            width: 24px;
            height: 24px;
        }}
        
        .nav {{
            display: flex;
            flex-direction: column;
            gap: 2px;
            padding: 0 8px;
        }}
        
        .nav-item {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 10px 16px;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.15s;
            font-size: 0.875rem;
            font-weight: 500;
            color: #666;
        }}
        
        .nav-item:hover {{ background: #f5f5f5; color: #1a1a1a; }}
        .nav-item.active {{ background: #1a1a1a; color: #fff; }}
        .nav-item .count {{ font-size: 0.75rem; opacity: 0.6; }}
        
        .main {{
            padding: 32px 40px;
            max-width: 860px;
        }}
        
        .header {{
            margin-bottom: 32px;
        }}
        
        .title {{
            font-size: 1.5rem;
            font-weight: 700;
            letter-spacing: -0.5px;
            margin-bottom: 4px;
        }}
        
        .subtitle {{
            color: #888;
            font-size: 0.85rem;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 12px;
            margin-bottom: 40px;
        }}
        
        .stat {{
            background: #fff;
            border: 1px solid #eee;
            border-radius: 10px;
            padding: 20px;
        }}
        
        .stat-num {{
            font-size: 1.75rem;
            font-weight: 700;
            letter-spacing: -1px;
        }}
        
        .stat-label {{
            font-size: 0.75rem;
            color: #888;
            text-transform: uppercase;
            letter-spacing: 0.3px;
            margin-top: 2px;
        }}
        
        .section {{ display: none; }}
        .section.active {{ display: block; }}
        
        .section-bar {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 16px;
        }}
        
        .section-title {{
            font-size: 1rem;
            font-weight: 600;
        }}
        
        .search {{
            width: 240px;
            padding: 8px 14px;
            border: 1px solid #e0e0e0;
            border-radius: 6px;
            font-family: inherit;
            font-size: 0.8rem;
            transition: border 0.2s;
        }}
        
        .search:focus {{ outline: none; border-color: #1a1a1a; }}
        
        .list {{
            background: #fff;
            border: 1px solid #eee;
            border-radius: 10px;
            overflow: hidden;
        }}
        
        .list-inner {{
            max-height: 480px;
            overflow-y: auto;
        }}
        
        .list-inner::-webkit-scrollbar {{ width: 3px; }}
        .list-inner::-webkit-scrollbar-thumb {{ background: #ddd; border-radius: 3px; }}
        
        .item {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 12px 18px;
            border-bottom: 1px solid #f5f5f5;
            text-decoration: none;
            color: inherit;
            transition: background 0.1s;
        }}
        
        .item:last-child {{ border-bottom: none; }}
        .item:hover {{ background: #fafafa; }}
        
        .item-info {{ min-width: 0; flex: 1; }}
        .item-name {{
            font-weight: 500;
            font-size: 0.875rem;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        
        .item-handle {{
            font-size: 0.75rem;
            color: #999;
            margin-top: 1px;
        }}
        
        .item-end {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .badge {{
            background: #1a1a1a;
            color: #fff;
            padding: 2px 7px;
            border-radius: 4px;
            font-size: 0.7rem;
            font-weight: 600;
        }}
        
        .arrow {{ color: #ccc; font-size: 0.75rem; }}
        .item:hover .arrow {{ color: #1a1a1a; }}
        
        .empty, .no-match {{
            padding: 50px 20px;
            text-align: center;
            color: #999;
            font-size: 0.85rem;
        }}
        
        .no-match {{ display: none; }}
        
        .footer {{
            margin-top: 50px;
            padding-top: 24px;
            border-top: 1px solid #eee;
            text-align: center;
            color: #888;
            font-size: 0.8rem;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 4px;
        }}
        
        .footer img.emoji {{
            height: 1em;
            width: 1em;
            vertical-align: -0.1em;
        }}
        
        @media (max-width: 860px) {{
            .app {{ grid-template-columns: 1fr; }}
            .sidebar {{ display: none; }}
            .main {{ padding: 24px 16px; }}
            .stats {{ grid-template-columns: repeat(2, 1fr); }}
            .search {{ width: 100%; }}
            .section-bar {{ flex-direction: column; gap: 12px; align-items: stretch; }}
        }}
    </style>
</head>
<body>
    <div class="app">
        <aside class="sidebar">
            <div class="logo">
                <svg class="logo-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M3 3v18h18"/>
                    <path d="M18 9l-5 5-4-4-3 3"/>
                </svg>
                TeleStats
            </div>
            <nav class="nav">
                <div class="nav-item active" onclick="show('overview')"><span>Overview</span></div>
                <div class="nav-item" onclick="show('channels')"><span>Channels</span><span class="count">{len(channels)}</span></div>
                <div class="nav-item" onclick="show('groups')"><span>Groups</span><span class="count">{len(groups)}</span></div>
                <div class="nav-item" onclick="show('chats')"><span>Private Chats</span><span class="count">{len(private_chats)}</span></div>
                <div class="nav-item" onclick="show('bots')"><span>Bots</span><span class="count">{len(bots)}</span></div>
            </nav>
        </aside>
        
        <main class="main">
            <div class="header">
                <h1 class="title">Dashboard</h1>
                <p class="subtitle">{datetime.now().strftime("%B %d, %Y · %H:%M")}</p>
            </div>
            
            <section class="section active" id="overview">
                <div class="stats">
                    <div class="stat"><div class="stat-num">{len(channels)}</div><div class="stat-label">Channels</div></div>
                    <div class="stat"><div class="stat-num">{len(groups)}</div><div class="stat-label">Groups</div></div>
                    <div class="stat"><div class="stat-num">{len(private_chats)}</div><div class="stat-label">Chats</div></div>
                    <div class="stat"><div class="stat-num">{len(bots)}</div><div class="stat-label">Bots</div></div>
                </div>
                <div class="section-bar"><h2 class="section-title">Recent</h2></div>
                <div class="list"><div class="list-inner">{generate_list_items(sorted(channels + groups + private_chats + bots, key=lambda x: x['unread'], reverse=True)[:10])}</div></div>
            </section>
            
            <section class="section" id="channels">
                <div class="section-bar">
                    <h2 class="section-title">Channels</h2>
                    <input type="text" class="search" placeholder="Search..." onkeyup="filter(this,'channels-list')">
                </div>
                <div class="list"><div class="list-inner" id="channels-list">{generate_list_items(channels) if channels else '<div class="empty">No channels</div>'}<div class="no-match">No results</div></div></div>
            </section>
            
            <section class="section" id="groups">
                <div class="section-bar">
                    <h2 class="section-title">Groups</h2>
                    <input type="text" class="search" placeholder="Search..." onkeyup="filter(this,'groups-list')">
                </div>
                <div class="list"><div class="list-inner" id="groups-list">{generate_list_items(groups) if groups else '<div class="empty">No groups</div>'}<div class="no-match">No results</div></div></div>
            </section>
            
            <section class="section" id="chats">
                <div class="section-bar">
                    <h2 class="section-title">Private Chats</h2>
                    <input type="text" class="search" placeholder="Search..." onkeyup="filter(this,'chats-list')">
                </div>
                <div class="list"><div class="list-inner" id="chats-list">{generate_list_items(private_chats) if private_chats else '<div class="empty">No chats</div>'}<div class="no-match">No results</div></div></div>
            </section>
            
            <section class="section" id="bots">
                <div class="section-bar">
                    <h2 class="section-title">Bots</h2>
                    <input type="text" class="search" placeholder="Search..." onkeyup="filter(this,'bots-list')">
                </div>
                <div class="list"><div class="list-inner" id="bots-list">{generate_list_items(bots) if bots else '<div class="empty">No bots</div>'}<div class="no-match">No results</div></div></div>
            </section>
            
            <div class="footer">Made with 💜 and too much ☕ by TheCHARITH</div>
        </main>
    </div>
    
    <script src="https://unpkg.com/twemoji@latest/dist/twemoji.min.js" crossorigin="anonymous"></script>
    <script>
        twemoji.parse(document.body, {{ folder: 'svg', ext: '.svg' }});
        
        function show(id) {{
            document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
            document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
            document.getElementById(id).classList.add('active');
            event.target.closest('.nav-item').classList.add('active');
        }}
        
        function filter(input, listId) {{
            const q = input.value.toLowerCase();
            const list = document.getElementById(listId);
            const items = list.querySelectorAll('.item');
            let c = 0;
            items.forEach(i => {{
                const match = i.textContent.toLowerCase().includes(q);
                i.style.display = match ? 'flex' : 'none';
                if (match) c++;
            }});
            list.querySelector('.no-match').style.display = c === 0 && q ? 'block' : 'none';
        }}
    </script>
</body>
</html>'''
    
    with open('telestats.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n📊 Stats:")
    print(f"   Channels: {len(channels)}")
    print(f"   Groups: {len(groups)}")
    print(f"   Private Chats: {len(private_chats)}")
    print(f"   Bots: {len(bots)}")
    print(f"\n✅ Dashboard saved as: telestats.html")
    print(f"🌐 Opening in browser...\n")
    
    webbrowser.open('file://' + os.path.realpath('telestats.html'))


def generate_list_items(items):
    html = ""
    for item in items:
        handle = f'@{item["username"]}' if item["username"] else ""
        badge = f'<span class="badge">{item["unread"]}</span>' if item["unread"] > 0 else ""
        html += f'''<a href="{item["link"]}" target="_blank" class="item"><div class="item-info"><div class="item-name">{item["name"]}</div><div class="item-handle">{handle}</div></div><div class="item-end">{badge}<span class="arrow">→</span></div></a>'''
    return html


if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(generate_dashboard())
