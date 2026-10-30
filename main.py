import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButtonRequestUser
import requests, sqlite3, re, time, json, threading, html as _html
from datetime import datetime, timedelta, timezone
_IST = timezone(timedelta(hours=5, minutes=30))

def _now_ist():
    return datetime.now(_IST).strftime('%d %b %Y %I:%M %p')
import os, random, string, io, sys, subprocess
import base64

def _safe_err(e):
    """Exception ko HTML-safe string mein convert karo"""
    return str(e).replace('<', '&lt;').replace('>', '&gt;')

def _strip_tg_emoji(text):
    """Remove Telegram premium/custom emoji entities while preserving their text."""
    try:
        text = re.sub(r'<tg-emoji\b[^>]*>(.*?)</tg-emoji>', r'\1', str(text), flags=re.DOTALL)
        return re.sub(r'</?tg-emoji\b[^>]*>', '', text)
    except Exception:
        return str(text)

def _safe_send(chat_id, text, **kwargs):
    """send_message with auto-fallback: strips tg-emoji if ENTITY_TEXT_INVALID."""
    try:
        return bot.send_message(chat_id, text, **kwargs)
    except Exception as _e:
        if 'entity_text_invalid' in str(_e).lower():
            try:
                return bot.send_message(chat_id, _strip_tg_emoji(text), **kwargs)
            except Exception as _e2:
                print(f'[SAFE_SEND] fallback failed: {_e2}')
        else:
            raise

def _send_react(chat_id, text, big=True, **kwargs):
    FREE_REACTIONS = ['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '\u200d', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '\u200d', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '\u200d', '', '\u200d', '']
    try:
        sent = bot.send_message(chat_id, text, **kwargs)
        try:
            random_emoji = random.choice(FREE_REACTIONS)
            bot.set_message_reaction(sent.chat.id, sent.message_id, [telebot.types.ReactionTypeEmoji(random_emoji)], is_big=big)
        except Exception as re:
            print(f'[REACTION ERROR] {re}')
        return sent
    except Exception as e:
        print(f'[SEND_REACT] {e}')
BOT_TOKEN = os.getenv('BOT_TOKEN', '8952108892:AAFuPvMRHa8-6crj6yFNZakEx6TX2VSxNh0')
OWNER_ID = int(os.getenv('NOT_CODER_OWNER_ID', '8803261206'))
FREE_CREDITS = 1
FREE_CREDITS_BOT = 1
FREE_CREDITS_GROUP = 1
REFERRAL_BONUS = 2

def _get_setting(key, default=''):
    try:
        r = c.execute('SELECT value FROM bot_settings WHERE key=?', (key,)).fetchone()
        return r[0] if r else default
    except:
        return default

def _set_setting(key, value):
    try:
        c.execute('INSERT OR REPLACE INTO bot_settings(key, value) VALUES(?,?)', (key, str(value)))
        conn.commit()
        return True
    except:
        return False

def get_referral_bonus():
    try:
        v = _get_setting('referral_bonus', str(REFERRAL_BONUS))
        return int(v)
    except:
        return REFERRAL_BONUS

def is_maintenance():
    return _get_setting('maintenance', '0') == '1'
LOG_CHANNEL_ID = -1003832254999
TOKEN_LOG_GROUP = -1004432003521
bot = telebot.TeleBot(BOT_TOKEN, threaded=True)
_orig_send_message = bot.send_message

def _patched_send_message(chat_id, text, **kwargs):
    try:
        return _orig_send_message(chat_id, text, **kwargs)
    except Exception as _e:
        if 'entity_text_invalid' in str(_e).lower():
            try:
                import re as _rp
                _clean = _rp.sub(r'<tg-emoji\b[^>]*>(.*?)</tg-emoji>', r'\1', str(text), flags=_rp.DOTALL)
                return _orig_send_message(chat_id, _clean, **kwargs)
            except Exception as _e2:
                print(f'[PATCH_SEND] fallback failed: {_e2}')
        raise
bot.send_message = _patched_send_message
_orig_reply_to = bot.reply_to

def _patched_reply_to(message, text, **kwargs):
    try:
        return _orig_reply_to(message, text, **kwargs)
    except Exception as _e:
        if 'entity_text_invalid' in str(_e).lower():
            try:
                import re as _rp
                _clean = _rp.sub(r'<tg-emoji\b[^>]*>(.*?)</tg-emoji>', r'\1', str(text), flags=_rp.DOTALL)
                return _orig_reply_to(message, _clean, **kwargs)
            except Exception as _e2:
                try:
                    return _orig_send_message(message.chat.id, _clean, **kwargs)
                except Exception as _e3:
                    print(f'[PATCH_REPLY] all fallbacks failed: {_e3}')
        raise
bot.reply_to = _patched_reply_to
_BOT_USERNAME_CACHE = None
_BOT_ID_CACHE = None

def _get_bot_username():
    global _BOT_USERNAME_CACHE
    if _BOT_USERNAME_CACHE:
        return _BOT_USERNAME_CACHE
    try:
        _BOT_USERNAME_CACHE = bot.get_me().username
    except:
        _BOT_USERNAME_CACHE = '𝙽𝚘𝚝 𝙲𝚘𝚍𝚎𝚛'
    return _BOT_USERNAME_CACHE

def _get_bot_id():
    global _BOT_ID_CACHE
    if _BOT_ID_CACHE:
        return _BOT_ID_CACHE
    try:
        _BOT_ID_CACHE = bot.get_me().id
    except:
        _BOT_ID_CACHE = int(BOT_TOKEN.split(':')[0])
    return _BOT_ID_CACHE
_F = '━━━━━━━━━━━━━━━━━━━━━━━━━━'

class _StyledKB(KeyboardButton):
    def __init__(self, text, style=None, **kwargs):
        super().__init__(text, **kwargs)
        self.__style = style
    def to_dict(self):
        d = super().to_dict()
        if self.__style:
            d['style'] = self.__style
        return d

class _StyledIKB(InlineKeyboardButton):
    def __init__(self, text, style=None, **kwargs):
        super().__init__(text, **kwargs)
        self.__style = 'success' if style == 'active' else style
    def to_dict(self):
        d = super().to_dict()
        if self.__style:
            d['style'] = self.__style
        return d

def _KB(text, style=None, **kwargs):
    if style == 'active':
        style = 'success'
    try:
        return _StyledKB(text, style=style, **kwargs)
    except:
        try:
            return KeyboardButton(text, **kwargs)
        except:
            return KeyboardButton(text)

def _IKB(text, style=None, **kwargs):
    try:
        return _StyledIKB(text, style=style, **kwargs)
    except:
        try:
            return InlineKeyboardButton(text, **kwargs)
        except:
            safe_kw = {k: v for k, v in kwargs.items() if k in ('callback_data', 'url', 'switch_inline_query', 'switch_inline_query_current_chat')}
            return InlineKeyboardButton(text, **safe_kw) if safe_kw else InlineKeyboardButton(text, callback_data='noop')
S_NONE = 'none'
S_NUM = 'number'
S_USER = 'username'
S_TID = 'tgid'
S_ADH = 'aadhar'
S_INSTA = 'instagram'
S_FF = 'freefire'
S_FFL = 'freefire_like'
S_VEH = 'vehicle'
S_REDEEM = 'redeem_code'
S_BOMB = 'bomber'
S_PREM_REDEEM = 'premium_redeem'
S_FF_LIKE_UID = 'ff_like_uid'
user_state = {}
_user_temp_cache = {}

def pbar(pct):
    """Progress bar: ▰▰▰▰▱▱▱▱▱▱▱▱▱▱▱  30%"""
    pct = max(0, min(100, int(pct)))
    total = 15
    filled = int(round(pct / 100 * total))
    empty = total - filled
    bar = '▰' * filled + '▱' * empty
    return f'{bar}  {pct}%'
_ANIM_PE = ""
_ANIM_STEPS = [(0, ' ᴄᴏɴɴᴇᴄᴛɪɴɢ...'), (8, ' ɪɴɪᴛɪᴀʟɪᴢɪɴɢ...'), (15, ' ʙʏᴩᴀꜱꜱɪɴɢ ꜱʏꜱᴛᴇᴍ...'), (22, ' ꜱᴇᴀʀᴄʜɪɴɢ ᴅᴀᴛᴀʙᴀꜱᴇ...'), (30, ' ꜰᴇᴛᴄʜɪɴɢ ᴀʟʟ ᴅᴀᴛᴀ...'), (40, ' ᴄᴏʟʟᴇᴄᴛɪɴɢ ɪɴꜰᴏ...'), (50, ' ᴘʀᴏᴄᴇꜱꜱɪɴɢ ʀᴇꜱᴜʟᴛꜱ...'), (60, ' ᴀɴᴀʟʏᴢɪɴɢ ᴅᴀᴛᴀ...'), (70, ' ᴠᴇʀɪꜰʏɪɴɢ ʀᴇᴄᴏʀᴅꜱ...'), (80, ' ꜰɪɴᴀʟɪᴢɪɴɢ...'), (88, ' ᴀʟᴍᴏꜱᴛ ᴅᴏɴᴇ...'), (95, ' ᴘʀᴇᴘᴀʀɪɴɢ ʀᴇꜱᴜʟᴛ...')]
_ANIM_LABELS = {'number': 'ꜰᴇᴛᴄʜɪɴɢ ɴᴜᴍʙᴇʀ ɪɴꜰᴏ...', 'username': 'ꜰᴇᴛᴄʜɪɴɢ ᴜꜱᴇʀɴᴀᴍᴇ ɪɴꜰᴏ...', 'tgid': 'ꜰᴇᴛᴄʜɪɴɢ ᴛɢ ɪᴅ ɪɴꜰᴏ...', 'aadhar': 'ꜰᴇᴛᴄʜɪɴɢ ...', 'instagram': 'ꜰᴇᴛᴄʜɪɴɢ ɪɴꜱᴛᴀ ɪɴꜰᴏ...', 'freefire': 'ꜰᴇᴛᴄʜɪɴɢ ꜰʀᴇᴇꜰɪʀᴇ ɪɴꜰᴏ...', 'like': 'ꜱᴇɴᴅɪɴɢ ʟɪᴋᴇꜱ...', 'viplike': 'ꜱᴇɴᴅɪɴɢ ᴠɪᴩ ʟɪᴋᴇꜱ...', 'bomber': 'ʟᴀᴜɴᴄʜɪɴɢ ʙᴏᴍʙᴇʀ...', 'vehicle': 'ꜰᴇᴛᴄʜɪɴɢ ...', 'usernum': 'ꜰᴇᴛᴄʜɪɴɢ ᴜꜱᴇʀ ɪɴꜰᴏ...'}

def _start_anim(chat_id, msg_id, label_key):
    '\n    Loading:\n        ▰▰▰▰▱▱▱▱▱▱▱▱▱▱▱  30%\n         ꜰᴇᴛᴄʜɪɴɢ ᴀʟʟ ᴅᴀᴛᴀ...\n    '
    final_label = _ANIM_LABELS.get(label_key, 'ꜰᴇᴛᴄʜɪɴɢ ᴀʟʟ ᴅᴀᴛᴀ...')
    stop_flag = [False]

    def _run():
        steps = list(_ANIM_STEPS) + [(82, f'⚡ {final_label}'), (88, f'⚡ {final_label}'), (92, f'⚡ {final_label}'), (95, f'⚡ {final_label}')]
        _i = 0
        _max = 40
        while not stop_flag[0] and _i < _max:
            if _i < len(steps):
                pct, msg_txt = steps[_i]
            else:
                pct, msg_txt = (95, f'⚡ {final_label}')
            try:
                bot.edit_message_text(f'<blockquote>{pbar(pct)}\n{msg_txt}</blockquote>', chat_id, msg_id, parse_mode='HTML')
            except:
                pass
            _i += 1
            time.sleep(0.55)
        if not stop_flag[0]:
            stop_flag[0] = True
            try:
                bot.edit_message_text(f'<blockquote>{pbar(0)}\n⚡ ʀᴇᴛʀʏɪɴɢ... {_ANIM_PE}</blockquote>', chat_id, msg_id, parse_mode='HTML')
            except:
                pass
    threading.Thread(target=_run, daemon=True).start()
    return stop_flag
LIKE_API_0 = 'https://simran-like-r-bot-api.vercel.app/like'
LIKE_API_1 = 'https://freefireautolikeservice.vercel.app/like'
LIKE_API_2 = 'https://ff-like-api-azure.vercel.app/like'
LIKE_API_3 = 'https://sexty-autolikes.vercel.app/like'
LIKE_API_4 = 'https://verma-like-api.vercel.app/like'
LIKE_API_5 = 'https://druu-likes-15-day.vercel.app/like'
FF_INFO_API = 'https://free-fire-info-bice.vercel.app/'
FF_INFO_KEY = 'SH4DAW-D4DY'
LIKE_COOLDOWN_HOURS = 12
LIKE_COOLDOWN_SECS = LIKE_COOLDOWN_HOURS * 3600
LIKE_DAILY_MAX = 10
uid_like_cooldown = {}
like_rate_limits = {}
VALID_REGIONS = ['ind', 'bd', 'id', 'th', 'vn', 'br', 'ru', 'my', 'sg', 'ph']
REGION_NAMES = {'ind': ' INDIA', 'bd': ' BANGLADESH', 'id': ' INDONESIA', 'th': ' THAILAND', 'vn': ' VIETNAM', 'br': ' BRAZIL', 'ru': ' RUSSIA', 'my': ' MALAYSIA', 'sg': ' SINGAPORE', 'ph': ' PHILIPPINES'}

def _like_check_cooldown(user_id, uid):
    if is_admin(user_id):
        return (True, 0, None)
    key = f'{user_id}:{uid}'
    now = time.time()
    if key in uid_like_cooldown:
        last = uid_like_cooldown[key].get('last_like', 0)
        elapsed = now - last
        if elapsed < LIKE_COOLDOWN_SECS:
            return (False, LIKE_COOLDOWN_SECS - elapsed, uid_like_cooldown[key])
    else:
        try:
            row = c.execute('SELECT last_like,uid,region,timestamp FROM ff_like_cooldown WHERE key=?', (key,)).fetchone()
            if row:
                last = row[0]
                elapsed = now - last
                info = {'last_like': last, 'uid': row[1], 'region': row[2], 'timestamp': row[3]}
                uid_like_cooldown[key] = info
                if elapsed < LIKE_COOLDOWN_SECS:
                    return (False, LIKE_COOLDOWN_SECS - elapsed, info)
        except:
            pass
    return (True, 0, None)

def _like_update_cooldown(user_id, uid, region):
    key = f'{user_id}:{uid}'
    now = time.time()
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    info = {'last_like': now, 'uid': uid, 'region': region, 'timestamp': ts}
    uid_like_cooldown[key] = info
    try:
        c.execute('INSERT OR REPLACE INTO ff_like_cooldown(key,user_id,uid,region,last_like,timestamp) VALUES(?,?,?,?,?,?)', (key, user_id, uid, region, now, ts))
        conn.commit()
    except:
        pass

def _like_check_ratelimit(user_id):
    if is_admin(user_id):
        return True
    key = f'{user_id}:like'
    now = time.time()
    if key not in like_rate_limits:
        try:
            row = c.execute('SELECT timestamps FROM ff_like_ratelimit WHERE key=?', (key,)).fetchone()
            if row and row[0]:
                like_rate_limits[key] = [float(t) for t in row[0].split(',') if t.strip()]
            else:
                like_rate_limits[key] = []
        except:
            like_rate_limits[key] = []
    like_rate_limits[key] = [t for t in like_rate_limits[key] if now - t < 86400]
    return len(like_rate_limits[key]) < LIKE_DAILY_MAX

def _like_update_ratelimit(user_id):
    if is_admin(user_id):
        return
    key = f'{user_id}:like'
    now = time.time()
    like_rate_limits.setdefault(key, []).append(now)
    like_rate_limits[key] = [t for t in like_rate_limits[key] if now - t < 86400]
    try:
        ts_str = ','.join((str(t) for t in like_rate_limits[key]))
        c.execute('INSERT OR REPLACE INTO ff_like_ratelimit(key,user_id,timestamps) VALUES(?,?,?)', (key, user_id, ts_str))
        conn.commit()
    except:
        pass

def _like_remaining_daily(user_id):
    if is_admin(user_id):
        return LIKE_DAILY_MAX
    key = f'{user_id}:like'
    now = time.time()
    if key not in like_rate_limits:
        try:
            row = c.execute('SELECT timestamps FROM ff_like_ratelimit WHERE key=?', (key,)).fetchone()
            if row and row[0]:
                like_rate_limits[key] = [float(t) for t in row[0].split(',') if t.strip()]
            else:
                like_rate_limits[key] = []
        except:
            like_rate_limits[key] = []
    used = len([t for t in like_rate_limits.get(key, []) if now - t < 86400])
    return max(0, LIKE_DAILY_MAX - used)
_db_lock = threading.Lock()
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_BOT_ID = BOT_TOKEN.split(':')[0]
_DB_FILE = os.path.join(_SCRIPT_DIR, f'bot_{_BOT_ID}.db')
conn = sqlite3.connect(_DB_FILE, check_same_thread=False)
conn.execute('PRAGMA journal_mode=WAL')
conn.execute('PRAGMA synchronous=NORMAL')
conn.commit()

class _SafeCursor:
    """Thread-safe cursor wrapper with one cursor per worker thread."""

    def __init__(self, connection):
        self._conn = connection
        self._lock = _db_lock
        self._local = threading.local()

    def _set_cursor(self, cur):
        self._local.cur = cur

    def _get_cursor(self):
        return getattr(self._local, 'cur', None)

    def execute(self, sql, params=()):
        with self._lock:
            cur = self._conn.cursor()
            cur.execute(sql, params)
            self._set_cursor(cur)
            return self

    def executescript(self, sql):
        with self._lock:
            cur = self._conn.cursor()
            cur.executescript(sql)
            self._set_cursor(cur)
            return self

    def executemany(self, sql, data):
        with self._lock:
            cur = self._conn.cursor()
            cur.executemany(sql, data)
            self._set_cursor(cur)
            return self

    def fetchone(self):
        cur = self._get_cursor()
        if cur is None:
            return None
        with self._lock:
            return cur.fetchone()

    def fetchall(self):
        cur = self._get_cursor()
        if cur is None:
            return []
        with self._lock:
            return cur.fetchall()

    @property
    def rowcount(self):
        cur = self._get_cursor()
        return cur.rowcount if cur is not None else 0
c = _SafeCursor(conn)
_orig_conn = conn

def _safe_commit():
    with _db_lock:
        try:
            _orig_conn.commit()
        except:
            pass

class _ConnWrapper:

    def __init__(self, c):
        self._c = c

    def __getattr__(self, name):
        if name == 'commit':
            return _safe_commit
        return getattr(self._c, name)
conn = _ConnWrapper(_orig_conn)
c.executescript("\nCREATE TABLE IF NOT EXISTS users(\n  user_id INTEGER PRIMARY KEY, username TEXT, first_name TEXT,\n  join_date TEXT, referrer INTEGER, credits INTEGER DEFAULT 5,\n  is_blocked INTEGER DEFAULT 0, is_premium INTEGER DEFAULT 0,\n  premium_until TEXT, joined_channel INTEGER DEFAULT 0, first_time INTEGER DEFAULT 1);\nCREATE TABLE IF NOT EXISTS referrals(\n  id INTEGER PRIMARY KEY AUTOINCREMENT, referrer INTEGER, referred INTEGER, date TEXT);\nCREATE TABLE IF NOT EXISTS bot_settings(\n  key TEXT PRIMARY KEY, value TEXT);\nCREATE TABLE IF NOT EXISTS scheduled_broadcasts(\n  id INTEGER PRIMARY KEY AUTOINCREMENT,\n  message TEXT, run_at TEXT, status TEXT DEFAULT 'pending',\n  created_by INTEGER, created_date TEXT);\nCREATE TABLE IF NOT EXISTS search_history(\n  id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, search_type TEXT,\n  query TEXT, search_date TEXT, result TEXT);\nCREATE TABLE IF NOT EXISTS daily_claims(\n  user_id INTEGER, claim_date TEXT, PRIMARY KEY(user_id,claim_date));\nCREATE TABLE IF NOT EXISTS redeem_codes(\n  id INTEGER PRIMARY KEY AUTOINCREMENT, code TEXT UNIQUE, credits INTEGER,\n  redeem_limit INTEGER, used_count INTEGER DEFAULT 0, created_by INTEGER,\n  created_date TEXT, expiry TEXT);\nCREATE TABLE IF NOT EXISTS redeemed_users(\n  code TEXT, user_id INTEGER, redeem_date TEXT, PRIMARY KEY(code,user_id));\nCREATE TABLE IF NOT EXISTS premium_codes(\n  id INTEGER PRIMARY KEY AUTOINCREMENT, code TEXT UNIQUE, days INTEGER,\n  redeem_limit INTEGER DEFAULT 1, used_count INTEGER DEFAULT 0, created_by INTEGER,\n  created_date TEXT, expiry TEXT);\nCREATE TABLE IF NOT EXISTS redeemed_premium(\n  code TEXT, user_id INTEGER, redeem_date TEXT, PRIMARY KEY(code,user_id));\nCREATE TABLE IF NOT EXISTS force_join_channels(\n  id INTEGER PRIMARY KEY AUTOINCREMENT, chat_id TEXT, chat_title TEXT,\n  chat_url TEXT, added_by INTEGER, added_date TEXT, is_active INTEGER DEFAULT 1);\nCREATE TABLE IF NOT EXISTS groups(\n  group_id INTEGER PRIMARY KEY, group_title TEXT, added_date TEXT, added_by INTEGER,\n  credits INTEGER DEFAULT 0, unlimited INTEGER DEFAULT 0,\n  is_blocked INTEGER DEFAULT 0, searches INTEGER DEFAULT 0, is_muted INTEGER DEFAULT 0);\nCREATE TABLE IF NOT EXISTS welcome_settings(\n  id INTEGER PRIMARY KEY CHECK(id=1), welcome_emoji TEXT DEFAULT '',\n  welcome_caption TEXT DEFAULT 'Welcome!',\n  welcome_image TEXT, welcome_video TEXT, bot_dp TEXT, first_time_sticker TEXT);\nCREATE TABLE IF NOT EXISTS blocked_identifiers(\n  id INTEGER PRIMARY KEY AUTOINCREMENT, identifier TEXT UNIQUE,\n  identifier_type TEXT, blocked_by INTEGER, blocked_date TEXT, reason TEXT);\nCREATE TABLE IF NOT EXISTS feature_toggles(\n  id INTEGER PRIMARY KEY AUTOINCREMENT, feature_name TEXT UNIQUE,\n  is_enabled INTEGER DEFAULT 1, updated_by INTEGER, updated_date TEXT);\nCREATE TABLE IF NOT EXISTS admins(\n  id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER UNIQUE,\n  added_by INTEGER, added_date TEXT, is_active INTEGER DEFAULT 1);\n\nCREATE TABLE IF NOT EXISTS token_log(\n  id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, user_name TEXT,\n  username TEXT, added INTEGER DEFAULT 0, total INTEGER DEFAULT 0,\n  source TEXT, bot_name TEXT, log_date TEXT, log_time TEXT);\nCREATE TABLE IF NOT EXISTS group_welcome_settings(\n  group_id INTEGER PRIMARY KEY, welcome_on INTEGER DEFAULT 1,\n  group_rules TEXT DEFAULT '', updated_date TEXT,\n  welcome_image TEXT, welcome_video TEXT, video_list TEXT);\n  CREATE TABLE IF NOT EXISTS verify_tokens(\n  user_id INTEGER, token TEXT UNIQUE, created_at TEXT);\nCREATE TABLE IF NOT EXISTS verify_claims(\n  id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER,\n  claim_date TEXT, UNIQUE(user_id, claim_date));\n")
conn.commit()

def safe_alter(tbl, col, typ, default='0'):
    try:
        c.execute(f'ALTER TABLE {tbl} ADD COLUMN {col} {typ} DEFAULT {default}')
        conn.commit()
    except:
        pass
safe_alter('groups', 'searches', 'INTEGER', '0')
safe_alter('group_welcome_settings', 'welcome_image', 'TEXT', 'NULL')
safe_alter('group_welcome_settings', 'welcome_video', 'TEXT', 'NULL')
safe_alter('group_welcome_settings', 'video_list', 'TEXT', 'NULL')
safe_alter('group_welcome_settings', 'group_sticker', 'TEXT', 'NULL')
safe_alter('group_welcome_settings', 'welcome_text', 'TEXT', 'NULL')
safe_alter('group_welcome_settings', 'bye_on', 'INTEGER', '1')
safe_alter('groups', 'unlimited', 'INTEGER', '0')
safe_alter('groups', 'is_blocked', 'INTEGER', '0')
safe_alter('groups', 'credits', 'INTEGER', '0')
safe_alter('groups', 'is_muted', 'INTEGER', '0')
safe_alter('force_join_channels', 'chat_type', 'TEXT', "'channel'")
safe_alter('force_join_channels', 'visibility', 'TEXT', "'public'")
try:
    conn._c.execute('CREATE TABLE IF NOT EXISTS user_fj_attempts(\n        user_id INTEGER PRIMARY KEY,\n        attempts INTEGER DEFAULT 0,\n        last_attempt TEXT)')
    _orig_conn.commit()
except:
    pass
try:
    conn._c.execute('CREATE TABLE IF NOT EXISTS api_keys(\n        id INTEGER PRIMARY KEY AUTOINCREMENT,\n        api_name TEXT UNIQUE,\n        api_url TEXT,\n        api_key TEXT,\n        is_active INTEGER DEFAULT 1,\n        added_by INTEGER,\n        added_date TEXT)')
    _orig_conn.commit()
except:
    pass
# Runtime state and safe defaults
FORCE_JOIN_DEFAULT_CHANNELS = [('', '', '')]
_admin_cache = {}
_feature_cache = {}
_user_cache = {}
_group_cache = {}
_channel_check_cache = {}
_CHANNEL_CACHE_TTL = 0
_PREM_EMOJI = ''
_MAIN_BOT_ACTIVE = True

def get_channels_keyboard(uid=None):
    """
    Force join buttons:
      Jᴏɪɴ Cʜᴀɴᴇʟ¹   Jᴏɪɴ Cʜᴀɴᴇʟ²
      ...
      last odd channel = single row
    Real join check — only unjoined channels shown.
    Channels from FORCE_JOIN_DEFAULT + admin panel DB.
    """
    chs = get_force_join_channels()
    if not chs:
        return None
    mk = InlineKeyboardMarkup()
    pending = []
    seen_btn = set()
    n = 0
    _sup = '⁰¹²³⁴⁵⁶⁷⁸⁹'

    def _sup_n(i):
        s = ''
        for ch in str(i):
            s += _sup[int(ch)] if ch.isdigit() else ch
        return s
    for entry in chs:
        cid_str = str(entry[0]).strip()
        title = entry[1] if len(entry) > 1 else 'Channel'
        url = entry[2] if len(entry) > 2 else ''
        nk = _fj_normalize(cid_str)
        if nk in seen_btn:
            continue
        seen_btn.add(nk)
        if not url:
            if cid_str.startswith('@'):
                url = f"https://t.me/{cid_str.lstrip('@')}"
            elif cid_str.startswith(('http://', 'https://')):
                url = cid_str
            else:
                # Numeric/private IDs without an explicit public link cannot produce
                # a usable Telegram join button. Leave them out instead of creating
                # a broken t.me/-100... URL.
                continue
        if uid and (not str(cid_str).startswith('https://')):
            try:
                cid_val = _resolve_chat_id(cid_str)
                if cid_val:
                    mem = bot.get_chat_member(cid_val, uid)
                    if mem.status not in ('left', 'kicked'):
                        continue
            except Exception:
                pass
        n += 1
        pending.append((url, n))
    if not pending:
        return None
    row = []
    for url, idx in pending:
        label = f'Jᴏɪɴ Cʜᴀɴᴇʟ{_sup_n(idx)}'
        row.append(_IKB(label, style='primary', url=url))
        if len(row) == 2:
            mk.row(*row)
            row = []
    if row:
        mk.row(*row)
    mk.row(_IKB(' Vᴇʀɪꜰʏ', style='success', callback_data='verify_channels'))
    return mk

def is_identifier_blocked(x):
    c.execute('SELECT COUNT(*) FROM blocked_identifiers WHERE identifier=?', (str(x).lower(),))
    return c.fetchone()[0] > 0

def block_identifier(x, t, by, r=''):
    try:
        c.execute('INSERT OR REPLACE INTO blocked_identifiers(identifier,identifier_type,blocked_by,blocked_date,reason) VALUES(?,?,?,?,?)', (str(x).lower(), t, by, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), r))
        conn.commit()
        return True
    except:
        return False

def unblock_identifier(x):
    try:
        c.execute('DELETE FROM blocked_identifiers WHERE identifier=?', (str(x).lower(),))
        conn.commit()
        return c.rowcount > 0
    except:
        return False

def get_blocked_identifiers():
    c.execute('SELECT identifier,identifier_type,blocked_date,reason FROM blocked_identifiers ORDER BY blocked_date DESC')
    return c.fetchall()





def generate_code():
    while True:
        code = f"NOT_CODER-{''.join(random.choices(string.ascii_uppercase + string.digits, k=6))}"
        c.execute('SELECT code FROM redeem_codes WHERE code=?', (code,))
        if not c.fetchone():
            return code

def generate_premium_code():
    while True:
        code = f"NOT_CODER_PR-{''.join(random.choices(string.ascii_uppercase + string.digits, k=6))}"
        c.execute('SELECT code FROM premium_codes WHERE code=?', (code,))
        if not c.fetchone():
            return code

def redeem_premium_code_fn(uid, code):
    code = code.upper().replace(' ', '').strip()
    candidates = [code]
    if not code.startswith('LPREM'):
        candidates.append('LPREM-' + code)
        candidates.append('LPREM' + code)
    r = None
    matched_code = code
    for cand in candidates:
        try:
            c.execute('SELECT code,days,redeem_limit,used_count FROM premium_codes WHERE UPPER(code)=?', (cand,))
            row = c.fetchone()
            if row:
                matched_code, days, rl, uc = (row[0], row[1], row[2], row[3])
                r = (days, rl, uc, None)
                break
        except Exception as e:
            print(f'[PREM_REDEEM_LOOKUP] {e}')
    if not r:
        return (False, ' Invalid premium code!\nUse code from admin (e.g. <code>LPREM-XXXXXX</code>)')
    days, rl, uc = (r[0], r[1], r[2])
    try:
        uc = int(uc or 0)
        rl = int(rl or 0)
        days = int(days)
    except Exception:
        return (False, ' Code data corrupt')
    try:
        c.execute('SELECT COUNT(*) FROM redeemed_premium WHERE UPPER(code)=? AND user_id=?', (matched_code.upper(), uid))
        if c.fetchone()[0] > 0:
            return (False, ' Already redeemed!')
    except Exception:
        pass
    if rl > 0 and uc >= rl:
        return (False, ' Code limit reached!')
    until = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')
    try:
        if not get_user(uid):
            add_user(uid, '', 'User')
        c.execute('UPDATE users SET is_premium=1, premium_until=? WHERE user_id=?', (until, uid))
        c.execute('UPDATE premium_codes SET used_count=COALESCE(used_count,0)+1 WHERE code=?', (matched_code,))
        try:
            c.execute('INSERT INTO redeemed_premium(code,user_id,redeem_date) VALUES(?,?,?)', (matched_code, uid, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        except Exception:
            try:
                c.execute('INSERT INTO redeemed_premium VALUES(?,?,?)', (matched_code, uid, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            except Exception as _ie:
                print(f'[PREM_INSERT] {_ie}')
        conn.commit()
        _user_cache.pop(uid, None)
        return (True, f'✅ Premium activated for <b>{days} days</b>!\n♾️ Unlimited credits till premium ends\n📅 Valid till: <code>{until}</code>')
    except Exception as e:
        print(f'[PREM_REDEEM] {e}')
        return (False, f'❌ Redeem failed: {_safe_err(e)}')

def redeem_code_fn(uid, code):
    code = code.upper().strip()
    if code.startswith('LPREM') or 'PREM' in code:
        return redeem_premium_code_fn(uid, code)
    try:
        c.execute('SELECT code FROM premium_codes WHERE UPPER(code)=?', (code,))
        if c.fetchone():
            return redeem_premium_code_fn(uid, code)
    except Exception:
        pass
    c.execute('SELECT credits,redeem_limit,used_count FROM redeem_codes WHERE code=?', (code,))
    r = c.fetchone()
    if not r:
        ok, msg = redeem_premium_code_fn(uid, code)
        if ok:
            return (ok, msg)
        return (False, ' Invalid redeem code!')
    cr, rl, uc = r
    c.execute('SELECT COUNT(*) FROM redeemed_users WHERE code=? AND user_id=?', (code, uid))
    if c.fetchone()[0] > 0:
        return (False, ' Already redeemed!')
    if rl > 0 and uc >= rl:
        return (False, ' Code limit reached!')
    if cr == -1:
        until = (datetime.now() + timedelta(days=3650)).strftime('%Y-%m-%d %H:%M:%S')
        update_user(uid, is_premium=1, premium_until=until)
        c.execute('UPDATE users SET credits=999999 WHERE user_id=?', (uid,))
        c.execute('UPDATE redeem_codes SET used_count=used_count+1 WHERE code=?', (code,))
        c.execute('INSERT INTO redeemed_users VALUES(?,?,?)', (code, uid, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()
        user = get_user(uid)
        try:
            bn = _get_bot_username()
        except:
            bn = 'bot'
        log_token_activity(uid, user[2] if user else 'User', user[1] if user else '', 'UNLIMITED', '∞', 'Redeem Unlimited Code', bn)
        return (True, ' <b>Unlimited credits</b> activated!')
    c.execute('UPDATE users SET credits=credits+? WHERE user_id=?', (cr, uid))
    c.execute('UPDATE redeem_codes SET used_count=used_count+1 WHERE code=?', (code,))
    c.execute('INSERT INTO redeemed_users VALUES(?,?,?)', (code, uid, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    conn.commit()
    user = get_user(uid)
    total = user[5] if user else cr
    try:
        bn = _get_bot_username()
    except:
        bn = 'bot'
    log_token_activity(uid, user[2] if user else 'User', user[1] if user else '', cr, total, 'Redeem Code Used', bn)
    return (True, f'✅ Redeemed <b>{cr}</b> credits!')

def check_blocked_and_reply(uid):
    if is_user_banned(uid):
        try:
            bot.send_message(uid, _BANNED_TEXT, parse_mode='HTML')
        except:
            pass
        return True
    return False

def safe_g(g, i, d=0):
    try:
        return g[i] if g and len(g) > i else d
    except:
        return d

def get_all_groups():
    try:
        return c.execute("SELECT group_id,group_title FROM groups ORDER BY LOWER(COALESCE(group_title,'')),group_id").fetchall()
    except Exception:
        return []

def add_group_to_db(gid,title,added_by=None):
    try:
        gid=int(gid); title=str(title or f'Group {gid}')[:255]
        by=int(added_by or OWNER_ID)
        now=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        c.execute('INSERT OR IGNORE INTO groups(group_id,group_title,added_date,added_by,credits,unlimited,is_blocked,searches,is_muted) VALUES(?,?,?,?,0,0,0,0,0)',(gid,title,now,by))
        c.execute('UPDATE groups SET group_title=? WHERE group_id=?',(title,gid))
        c.execute("INSERT OR IGNORE INTO group_welcome_settings(group_id,welcome_on,group_rules,updated_date) VALUES(?,1,'',?)",(gid,now))
        conn.commit(); _group_cache.pop(gid,None)
        return True
    except Exception as e:
        print(f'[ADD_GROUP] {e}'); return False

def get_group(gid):
    if gid in _group_cache:
        return _group_cache[gid]
    c.execute('SELECT * FROM groups WHERE group_id=?', (gid,))
    row = c.fetchone()
    _group_cache[gid] = row
    return row

def is_group_muted(gid):
    g = get_group(gid)
    return safe_g(g, 8) == 1 if g else False

def toggle_group_mute(gid):
    g = get_group(gid)
    if g:
        nv = 0 if safe_g(g, 8) == 1 else 1
        c.execute('UPDATE groups SET is_muted=? WHERE group_id=?', (nv, gid))
        conn.commit()
        return nv == 1
    return False

def deduct_group_credit(gid):
    """Group credit system — sirf searches count karo. Credit system user-based hai."""
    _group_cache.pop(gid, None)
    g = get_group(gid)
    if not g:
        return True
    if safe_g(g, 6) == 1:
        return False
    try:
        c.execute('UPDATE groups SET searches=searches+1 WHERE group_id=?', (gid,))
        conn.commit()
    except:
        pass
    _group_cache.pop(gid, None)
    return True

def refund_group_credit(gid):
    """Group credit refund — noop, user credits se hi kaam hota hai"""
    pass

def toggle_group_unlimited(gid):
    _group_cache.pop(gid, None)
    g = get_group(gid)
    if g:
        nv = 0 if safe_g(g, 5) == 1 else 1
        c.execute('UPDATE groups SET unlimited=? WHERE group_id=?', (nv, gid))
        conn.commit()
        _group_cache.pop(gid, None)
        return nv == 1
    return False

def toggle_group_block(gid):
    _group_cache.pop(gid, None)
    g = get_group(gid)
    if g:
        nv = 0 if safe_g(g, 6) == 1 else 1
        c.execute('UPDATE groups SET is_blocked=? WHERE group_id=?', (nv, gid))
        conn.commit()
        _group_cache.pop(gid, None)
        return nv == 1
    return False

def add_group_credits_fn(gid, cr):
    c.execute('UPDATE groups SET credits=credits+? WHERE group_id=?', (cr, gid))
    conn.commit()
    _group_cache.pop(gid, None)

def rem_group_credits_fn(gid, cr):
    c.execute('UPDATE groups SET credits=MAX(0,credits-?) WHERE group_id=?', (cr, gid))
    conn.commit()
    _group_cache.pop(gid, None)

def log_token_activity(uid, user_name, username_tg, added, total, source, bot_name=None):
    """TOKEN LOG -> @database𝙽𝚘𝚝 𝙲𝚘𝚍𝚎𝚛 - all events: join, left, credit, bomber, pan, redeem etc."""
    try:
        if not bot_name:
            try:
                bot_name = _get_bot_username()
            except:
                bot_name = '𝙽𝚘𝚝 𝙲𝚘𝚍𝚎𝚛_bot'
        udisp = f'@{username_tg}' if username_tg else 'No Username'
        now = datetime.now()
        ld = now.strftime('%d %b %Y')
        lt = now.strftime('%I:%M %p')
        c.execute('INSERT INTO token_log(user_id,user_name,username,added,total,source,bot_name,log_date,log_time) VALUES(?,?,?,?,?,?,?,?,?)', (uid, user_name, username_tg or '', added, total, source, bot_name, ld, lt))
        conn.commit()
        src_lower = source.lower()
        if 'join' in src_lower:
            icon = ''
            event_type = 'JOIN'
        elif 'left' in src_lower or 'leave' in src_lower:
            icon = ''
            event_type = 'LEFT'
        elif 'bomber' in src_lower:
            icon = ''
            event_type = 'BOMBER'
        elif 'pan' in src_lower:
            icon = ''
            event_type = 'PAN SEARCH'
        elif 'redeem' in src_lower:
            icon = ''
            event_type = 'REDEEM'
        elif 'spin' in src_lower:
            icon = ''
            event_type = 'DAILY SPIN'
        elif 'referral' in src_lower or 'refer' in src_lower:
            icon = ''
            event_type = 'REFERRAL'
        elif 'premium' in src_lower:
            icon = ''
            event_type = 'PREMIUM'
        elif 'credit' in src_lower:
            icon = ''
            event_type = 'CREDITS'
        else:
            icon = ''
            event_type = 'ACTIVITY'
        _LS = _SEP()
        _LE = _SEP()
        txt = f"<blockquote>{icon} <b>TOKEN LOG</b> — {event_type}\n\n👤 ᴜꜱᴇʀ    : {user_name}\n🆔 ɪᴅ      : <code>{uid}</code>\n🔗 ᴜꜱᴇʀɴᴀᴍᴇ: {udisp}\n\n{_LS}\n{(' ᴀᴅᴅᴇᴅ  : ' + str(added) + ' ᴄʀᴇᴅɪᴛ' + chr(10) if added else '')}{(' ᴛᴏᴛᴀʟ  : ' + str(total) + ' ᴄʀᴇᴅɪᴛ' + chr(10) if total else '')}🏷️ ꜱᴏᴜʀᴄᴇ  : {source}\n{_LS}\n🤖 ʙᴏᴛ     : @{bot_name}\n📅 ᴅᴀᴛᴇ    : {ld}\n🕒 ᴛɪᴍᴇ    : {lt}\n{_LE}\n </blockquote>"
        bot.send_message(TOKEN_LOG_GROUP, txt, parse_mode='HTML')
    except Exception as e:
        print(f'[TOKEN_LOG] Error: {_safe_err(e)}')

def log_search(uid, uname, tgname, stype, query, photo=None):
    """Log search to @basefoli"""
    try:
        try:
            bn = _get_bot_username()
        except:
            bn = '𝙽𝚘𝚝 𝙲𝚘𝚍𝚎𝚛_bot'
        udisp = f'@{tgname}' if tgname else 'No Username'
        _LS2 = _SEP()
        _LE2 = _SEP()
        txt = f"<blockquote>╭━━━━━━━━━━━━━━━✦\n│ 📊 <b>𝗧𝗢𝗞𝗘𝗡 𝗟𝗢𝗚</b>\n╰━━━━━━━━━━━━━━━✦\n\n👤 {uname}\n🆔 {uid}\n🔗 {udisp}\n\n{_LS2}\n🔍 <b>{stype.upper()}</b>\n📝 <code>{query}</code>\n{_LS2}\n🤖 @{bn}\n📅 {datetime.now().strftime('%d %b %Y')}\n🕒 {datetime.now().strftime('%I:%M %p')}\n{_LE2}\n⚡ @notCoder2006\n</blockquote>"
        if photo and isinstance(photo, str) and photo.startswith('http'):
            try:
                bot.send_photo(LOG_CHANNEL_ID, photo, caption=txt, parse_mode='HTML')
                return
            except:
                pass
        bot.send_message(LOG_CHANNEL_ID, txt, parse_mode='HTML')
    except Exception as e:
        print(f'[SEARCH_LOG] {_safe_err(e)}')
_welcome_settings_cache = None
_welcome_fileid_cache = {}
_group_video_fileid_cache = {}

def get_welcome_settings():
    global _welcome_settings_cache
    c.execute('SELECT * FROM welcome_settings WHERE id=1')
    _welcome_settings_cache = c.fetchone()
    return _welcome_settings_cache

def _invalidate_welcome_cache():
    global _welcome_settings_cache
    _welcome_settings_cache = None
    _welcome_fileid_cache.clear()

def get_first_time_sticker():
    c.execute('SELECT first_time_sticker FROM welcome_settings WHERE id=1')
    r = c.fetchone()
    return r[0] if r else None
_SPIN_EMOJIS = ['', '', '', '', '']

def _get_spin_emoji():
    """Har spin pe randomly ek emoji choose karo"""
    return random.choice(_SPIN_EMOJIS)

def format_welcome(uid, fname, credits, username=''):
    fname = _html.escape(fname)
    udisp = f'@{username}' if username else 'ɴᴏ ᴜꜱᴇʀɴᴀᴍᴇ'
    cr_disp = '∞' if is_admin(uid) else str(credits)
    try:
        bn = _get_bot_username()
    except:
        bn = '𝙽𝚘𝚝 𝙲𝚘𝚍𝚎𝚛RDX_bot'
    try:
        ref_count = get_referral_count(uid)
    except Exception:
        ref_count = 0
    status_txt = 'ꜰʀᴇᴇ ᴜꜱᴇʀ'
    try:
        c.execute('SELECT is_premium,premium_until FROM users WHERE user_id=?', (uid,))
        row = c.fetchone()
        if row and row[0] == 1:
            if row[1]:
                try:
                    if datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S') > datetime.now():
                        status_txt = 'ᴘʀᴇᴍɪᴜᴍ ᴜꜱᴇʀ'
                except Exception:
                    status_txt = 'ᴘʀᴇᴍɪᴜᴍ ᴜꜱᴇʀ'
            else:
                status_txt = 'ᴘʀᴇᴍɪᴜᴍ ᴜꜱᴇʀ'
        if is_admin(uid):
            status_txt = 'ᴘʀᴇᴍɪᴜᴍ ᴜꜱᴇʀ'
    except Exception:
        if is_admin(uid):
            status_txt = 'ᴘʀᴇᴍɪᴜᴍ ᴜꜱᴇʀ'

    def te(e, fallback='⭐'):
        return f"{fallback}"
    e_spark = te('6325336377068100031', '')
    e_cat = te('6293791019100019997', '')
    e_gift1 = te('5422649648630233281', '')
    e_heart = te('5323621257701254783', '')
    e_note = te('5231280190981696917', '')
    e_bottle = te('5278433859535385490', '')
    e_gift2 = te('5422627838786306160', '')
    e_brick = te('5326049357332513437', '')
    e_chain = te('6097974883025688046', '')
    e_star = te('5411218262459445111', '⭐')
    e_wow = te('5773659712071409251', '')
    e_gift3 = te('6100459890973612423', '')
    e_drink = te('6293819056646528302', '')
    e_flower = te('6190636289881021566', '')
    dev_line = f'{e_gift3} ⇛ Dᴇᴠʟᴏᴩᴇʀ :- @notCoder2006 {e_drink}'
    return f"<blockquote>{e_spark} ╭── [ {e_cat} ꜱ ʏ ꜱ ᴛ ᴇ ᴍ  ɪ ɴ ɪ ᴛ ɪ ᴀ ᴛ ᴇ ᴅ {e_gift1} ]\n│\n├── {e_heart} ⇛ ʜᴇʏ <a href='tg://user?id={uid}'><b>{fname}</b></a>\n├── {e_note} ⇛ ɪ ᴀᴍ @{bn}\n├── {e_bottle} ⇛ ᴍᴏꜱᴛ ᴩᴏᴡᴇʀꜰᴜʟʟ ᴏꜱɪɴᴛ\n│\n├── [ {e_gift2} ʏ ᴏ ᴜ ʀ  ꜱ ᴛ ᴀ ᴛ ᴜ ꜱ ]\n├── {e_brick} ⇛ Cʀᴇᴅɪᴛ :- {cr_disp}\n├── {e_chain} ⇛ Rᴇꜰᴇʀꜱ :- {ref_count}\n├── {e_star} ⇛ Sᴛᴀᴛᴜꜱ :- {e_wow} {status_txt}\n├── {dev_line}\n│\n{e_flower} ╰── ᴩʀᴇꜱꜱ ʜᴇʟᴩ ᴛᴏ ᴇxᴩʟᴏʀᴇ ᴍᴏʀᴇ ᴄᴏᴍᴍᴀɴᴅꜱ !</blockquote>"


def _welcome_media_caption(uid,fname,username,credits,default_text):
    try:
        st=get_welcome_settings(); raw=(st[2] if st and len(st)>2 else '') or ''
        if not raw or raw.strip()=='Welcome!': return default_text
        vals={'name':_html.escape(fname or 'User'),'id':str(uid),'username':_html.escape('@'+username if username else 'No Username'),'credits':str(credits)}
        return raw.format(**vals)
    except Exception:
        return default_text

def no_credits_msg(uid):
    try:
        ref = f'https://t.me/{_get_bot_username()}?start={uid}'
    except:
        ref = f'https://t.me/bot?start={uid}'
    cr = get_credits(uid)
    try:
        ref_count = get_referral_count(uid)
    except Exception:
        ref_count = 0
    try:
        total_earn = int(ref_count) * int(get_referral_bonus())
    except Exception:
        total_earn = 0

    def te(eid, fb='⭐'):
        return f"{fb}"
    e_loop = te('5465270065102334742', '')
    e_money = te('6267068789146260253', '')
    e_chain = te('6001078118725456537', '')
    e_phone = te('5406809207947142040', '')
    e_coin = te('6089104607328342288', '')
    e_link = te('5983262173474853675', '')
    e_down = te('5470177992950946662', '')
    e_ok = te('5213395028038132311', '')
    L11 = e_loop * 11
    L6 = e_loop * 6
    txt = f'<blockquote>{L11}\n{e_money} <b>𝗥𝗲𝗳𝗲𝗿 & 𝗲𝗮𝗿𝗻</b> {e_chain}\n{L11}\n\n{e_phone} ᴛᴏᴛᴀʟ ʀᴇꜰᴇʀꜱ : <b>{ref_count}</b> Fʀɪᴇɴᴅꜱ\n{e_coin} Tᴏᴛᴀʟ Eᴀʀɴ :- <b>{total_earn}</b> Cʀᴇᴅɪᴛ\n\n{L6}\n{e_link} ʏᴏᴜʀ ʀᴇꜰᴇʀʀᴀʟ ʟɪɴᴋ:\n<code>{ref}</code>\n\n{L6}\n{e_down} Tᴀᴩ ᴛᴏ Rᴇꜰᴇʀ ᴛᴏ Fʀɪᴇɴᴅ {e_ok}:</blockquote>'
    mk = InlineKeyboardMarkup(row_width=2)
    mk.row(_IKB('ꜱʜᴀʀᴇ ʟɪɴᴋ', style='success', url=f'https://t.me/share/url?url={ref}&amp;text=Join+this+bot+and+get+free+credits!'), _IKB('ɢᴇᴛ ᴀᴄᴄᴇꜱꜱ', style='primary', callback_data='show_premium_plans'))
    return (txt, mk)

def get_pic(d):
    """Try every possible key for profile picture"""
    if not d:
        return None
    keys = ['profile_pic', 'profile_picture', 'png_link', 'photo', 'pic', 'pfp', 'avatar', 'image', 'profilePic', 'profilePicture', 'profile_photo', 'pp', 'thumbnail', 'display_pic']
    for k in keys:
        v = d.get(k)
        if v and isinstance(v, str) and v.startswith('http'):
            return v
    ud = d.get('data', {})
    if isinstance(ud, dict):
        for k in keys:
            v = ud.get(k)
            if v and isinstance(v, str) and v.startswith('http'):
                return v
    return None

def _safe_caption(text, limit=1024):
    """Caption ke liye safe HTML — tg-emoji strip karo, limit ke andar rakho, tags close karo."""
    import re as _rc
    stripped = _rc.sub(']*>.*?', '', text, flags=_rc.DOTALL)
    stripped = _rc.sub('</tg-emoji>', '', stripped)
    stripped = _rc.sub(']*>', '', stripped)
    if len(stripped) <= limit:
        return stripped
    cut = stripped[:limit]
    cut = _rc.sub('<[^>]*$', '', cut)
    _TAGS = ('blockquote', 'b', 'i', 'code', 'a', 'pre')
    opened_all = _rc.findall('<(blockquote|b|i|code|a|pre)[\\s>/]', cut)
    closed_all = _rc.findall('</(blockquote|b|i|code|a|pre)>', cut)
    to_close = list(reversed(opened_all))
    closed_counts = {t: closed_all.count(t) for t in _TAGS}
    open_counts = {t: opened_all.count(t) for t in _TAGS}
    suffix = ''
    for tag in to_close:
        if closed_counts.get(tag, 0) < open_counts.get(tag, 0):
            suffix += f'</{tag}>'
            open_counts[tag] -= 1
    return cut + suffix

def send_with_pfp(chat_id, text, pic, del_msg_id=None):
    sent = False
    if not pic:
        m_id = re.search('tg://user[?]id=(\\d+)', text)
        if m_id:
            tid = m_id.group(1)
            try:
                pic = _fetch_pfp_by_id(tid)
            except:
                pic = None
            if not pic:
                pic = f'http://username-to-info-rwsw.onrender.com/media/{tid}.png'
    if pic and isinstance(pic, str) and pic.startswith('http'):
        try:
            img_bytes = requests.get(pic, timeout=10).content
            if img_bytes and len(img_bytes) > 1000:
                if del_msg_id:
                    try:
                        bot.delete_message(chat_id, del_msg_id)
                    except:
                        pass
                bio = io.BytesIO(img_bytes)
                bio.seek(0)
                caption = _safe_caption(text, 1024)
                bot.send_photo(chat_id, bio, caption=caption, parse_mode='HTML')
                sent = True
        except Exception as e:
            print(f'[PFP] {_safe_err(e)}')
    if not sent:
        if del_msg_id:
            try:
                bot.edit_message_text(text, chat_id, del_msg_id, parse_mode='HTML')
                return
            except:
                try:
                    bot.delete_message(chat_id, del_msg_id)
                except:
                    pass
        try:
            bot.send_message(chat_id, text, parse_mode='HTML')
        except:
            pass
ABDULSTORE_API_KEY = 'ak_59eca148e4484ccb50e8575645c32ee1'

def _K(key_name):
    """Dynamic API key getter — DB custom ya default"""
    try:
        return _get_live_api_key(key_name)
    except:
        pass
    _defaults = {'key_sh4daw': 'SH4DAW-D4DY', 'key_abdulstore': 'ak_59eca148e4484ccb50e8575645c32ee1', 'key_ff_info': 'SH4DAW-D4DY', 'key_rlx_bomber': 'rlxcoder', 'key_numinfo': 'SH4DAW-D4DY', 'key_aadhar': 'SH4DAW-D4DY', 'key_instagram': 'SH4DAW-D4DY', 'key_vehicle': 'SH4DAW-D4DY', 'key_username': 'SH4DAW-D4DY'}
    return _defaults.get(key_name, '')
ABDULSTORE_API_URL = 'https://store.abdulstoreapi.workers.dev/api/v1'
_LUFFY_API_BASE = 'https://testing-apis-1.onrender.com/api'
_LUFFY_API_KEY = 'LUFFY09'

def _luffy_get(params, timeout=25):
    """Call testing-apis-1 and return parsed JSON or None"""
    try:
        p = dict(params)
        p['key'] = _LUFFY_API_KEY
        r = requests.get(_LUFFY_API_BASE, params=p, timeout=timeout)
        if r.status_code != 200:
            return None
        try:
            return r.json()
        except Exception:
            return None
    except Exception as e:
        print(f'[LUFFY_API] {e}')
        return None

def _luffy_norm_num_list(raw, num):
    """Normalize list/dict from LUFFY num/aadhar APIs to bot fmt_number_page style"""
    recs = []
    if isinstance(raw, list):
        recs = raw
    elif isinstance(raw, dict):
        if isinstance(raw.get('data'), list):
            recs = raw['data']
        elif raw.get('name') or raw.get('num') or raw.get('mobile'):
            recs = [raw]
        elif raw.get('error') or raw.get('message'):
            return None
    norm = []
    for rec in recs:
        if not isinstance(rec, dict):
            continue
        norm.append({'name': (rec.get('name') or 'N/A').strip() if isinstance(rec.get('name'), str) else rec.get('name') or 'N/A', 'fname': rec.get('fname') or rec.get('father_name') or '', 'address': rec.get('address') or '', 'mobile': rec.get('mobile') or rec.get('num') or num, 'alt': rec.get('alt') or rec.get('alt_number') or '', 'circle': rec.get('circle') or '', 'email': rec.get('email') or '', 'id': rec.get('id') or rec.get('aadhar') or ''})
    if not norm:
        return None
    return {'success': True, '_api_source': 'luffy_api', 'data': norm, 'total_records': len(norm)}

def _luffy_norm_tg(raw, query):
    """Normalize TG response for _fmt_tg_user"""
    if not raw or not isinstance(raw, dict):
        return None
    if raw.get('error') or (raw.get('message') and (not raw.get('phone')) and (not raw.get('number')) and (not raw.get('telegram_id')) and (not raw.get('id'))):
        pass
    phone = str(raw.get('phone') or raw.get('number') or raw.get('mobile') or raw.get('num') or '').strip()
    if phone in ('N/A', 'None', 'null', '-'):
        phone = ''
    tg_id = str(raw.get('telegram_id') or raw.get('tg_id') or raw.get('id') or raw.get('user_id') or '').strip()
    if not tg_id and str(query).lstrip('-').isdigit():
        tg_id = str(query).strip()
    ud = {'telegram_id': tg_id, 'first_name': raw.get('first_name') or raw.get('name') or '', 'last_name': raw.get('last_name') or '', 'username': (raw.get('username') or '').replace('@', ''), 'phone': phone, 'number': phone}
    ok = bool(phone or tg_id or ud['first_name'] or ud['username']) and (not (raw.get('error') and (not phone) and (not tg_id)))
    if raw.get('message') and 'Could not resolve' in str(raw.get('message')) and (not phone):
        ok = False
    return {'success': ok, 'phone': phone or 'N/A', 'telegram_id': tg_id, 'target_id': tg_id, 'data': ud, 'response_time': str(raw.get('response_time') or ''), '_api_source': 'luffy_api'}

def _luffy_norm_veh(raw, rc):
    if not raw or not isinstance(raw, dict):
        return None
    if raw.get('error') and (not (raw.get('owner_name') or raw.get('owner') or raw.get('name'))):
        return None
    return {'success': True, 'rc_number': raw.get('rc_number') or raw.get('rc') or rc, 'owner_name': raw.get('owner_name') or raw.get('owner') or raw.get('name') or 'N/A', 'mobile_number': raw.get('mobile_number') or raw.get('mobile') or raw.get('num') or raw.get('phone') or 'N/A', 'vehicle_model': raw.get('vehicle_model') or raw.get('model') or raw.get('vehicle') or 'N/A', 'registration_date': raw.get('registration_date') or raw.get('reg_date') or 'N/A', 'fuel_type': raw.get('fuel_type') or raw.get('fuel') or 'N/A', 'engine_number': raw.get('engine_number') or raw.get('engine') or 'N/A', 'chassis_number': raw.get('chassis_number') or raw.get('chassis') or 'N/A', 'insurance_valid_till': raw.get('insurance_valid_till') or raw.get('insurance') or 'N/A', 'tax_valid_till': raw.get('tax_valid_till') or raw.get('tax') or 'N/A', '_api_source': 'luffy_api'}

NUMINFO_API_URL = os.getenv('NUMINFO_API_URL', 'https://num-info.noobster11001.workers.dev')
NUMINFO_API_KEY = os.getenv('NUMINFO_API_KEY', '@noob11001')

def _clean_na(val):
    """API ke 'NA' / 'N/A' / None / '-' values ko empty string mein convert karo"""
    if val is None:
        return ''
    s = str(val).strip()
    if s.upper() in ('NA', 'N/A', 'NONE', 'NULL', '-', '—', ''):
        return ''
    return s


def _clean_address(addr):
    """Address mein '!' ko ', ' se replace karo aur 'NA' parts hatao"""
    s = _clean_na(addr)
    if not s:
        return ''
    parts = [p.strip() for p in re.split(r'[!,]+', s) if _clean_na(p)]
    return ', '.join(parts)


def api_number(num):
    """
    Number Info lookup via num-info.noobster11001.workers.dev
    Response structure:
      { success, number, timestamp,
        hiteck_info: { data: {name, fname, mobile, alt, circle, address, email, id}, ... },
        icmr_info: { data/error, ... } }
    API developer credits (Api_by/Channel) ko IGNORE karte hain.
    """
    num = re.sub(r'\D', '', str(num or ''))
    if not re.fullmatch(r'[6-9]\d{9}', num):
        return {
            'success': False,
            '_api_source': 'numinfo',
            'data': [],
            'total_records': 0,
            'message': 'Invalid number',
        }

    try:
        resp = requests.get(
            NUMINFO_API_URL,
            params={'key': NUMINFO_API_KEY, 'num': num},
            headers={'Accept': 'application/json'},
            timeout=20,
        )
        if resp.status_code != 200:
            print(f'[NUMINFO_API] HTTP {resp.status_code}: {resp.text[:200]}')
            return {
                'success': False,
                '_api_source': 'numinfo',
                'data': [],
                'total_records': 0,
                'message': f'HTTP {resp.status_code}',
            }

        try:
            payload = resp.json()
        except ValueError as exc:
            print(f'[NUMINFO_API] Invalid JSON: {exc}')
            return {
                'success': False,
                '_api_source': 'numinfo',
                'data': [],
                'total_records': 0,
                'message': 'Invalid JSON response',
            }

        if not isinstance(payload, dict):
            return {
                'success': False,
                '_api_source': 'numinfo',
                'data': [],
                'total_records': 0,
                'message': 'Invalid response format',
            }

        # ✅ Extract data — hiteck_info primary, icmr_info fallback
        normalized = []
        for src_key in ('hiteck_info', 'icmr_info'):
            src = payload.get(src_key) or {}
            if not isinstance(src, dict):
                continue
            src_data = src.get('data')
            if not isinstance(src_data, dict) or not src_data:
                continue

            name = _clean_na(src_data.get('name'))
            mobile = _clean_na(src_data.get('mobile')) or num
            # Sirf tab add karo jab actual naam ya mobile ho
            if not name and not mobile:
                continue

            normalized.append({
                'mobile': mobile,
                'name':   name or 'N/A',
                'fname':  _clean_na(src_data.get('fname')),
                'alt':    _clean_na(src_data.get('alt')),
                'circle': _clean_na(src_data.get('circle')),
                'address': _clean_address(src_data.get('address')),
                'email':  _clean_na(src_data.get('email')),
                'id':     _clean_na(src_data.get('id')),
            })

        api_success = bool(payload.get('success')) and bool(normalized)
        return {
            'success': api_success,
            '_api_source': 'numinfo',
            'data': normalized,
            'total_records': len(normalized),
        }

    except requests.RequestException as exc:
        print(f'[NUMINFO_API] Request failed: {exc}')
    except Exception as exc:
        print(f'[NUMINFO_API] {exc}')

    return {
        'success': False,
        '_api_source': 'numinfo',
        'data': [],
        'total_records': 0,
        'message': 'API request failed',
    }

def _merge_from_un_api(d2):
    """Flatten ALL fields from username API response into one dict"""
    _str_only = {'username', 'first_name', 'last_name', 'bio', 'phone', 'number', 'country', 'country_code'}
    flat = {}
    for key in ['info', 'data', 'result', 'user', 'profile']:
        sub = d2.get(key, {})
        if isinstance(sub, dict):
            flat.update(sub)
            inner = sub.get('data', {})
            if isinstance(inner, dict):
                flat.update(inner)
    for k, v in d2.items():
        if v not in (None, ''):
            if k in _str_only and (not isinstance(v, str)):
                continue
            flat[k] = v
    return flat

def _fetch_pfp_by_id(uid_str):
    """Telegram Bot API se directly PFP fetch karo — file_id wapas karo (bytes nahi)"""
    try:
        r = requests.get(f'https://api.telegram.org/bot{BOT_TOKEN}/getUserProfilePhotos', params={'user_id': uid_str, 'limit': 1}, timeout=8)
        if r.status_code == 200:
            photos = r.json().get('result', {}).get('photos', [])
            if photos and photos[0]:
                fid = photos[0][-1].get('file_id', '')
                if fid:
                    r2 = requests.get(f'https://api.telegram.org/bot{BOT_TOKEN}/getFile', params={'file_id': fid}, timeout=8)
                    if r2.status_code == 200:
                        fpath = r2.json().get('result', {}).get('file_path', '')
                        if fpath:
                            return f'https://api.telegram.org/file/bot{BOT_TOKEN}/{fpath}'
    except Exception as e:
        print(f'[PFP] {_safe_err(e)}')
    return None

def _call_un_api(username):
    """
    Username INFO — ONLY user-to-num-info-zcpe.onrender.com + TG getChat
    """
    cl = username.replace('@', '').strip()
    flat = {}
    pic = None
    tg_id_found = ''
    import concurrent.futures as _cf_un

    def _fetch_new_api():
        try:
            r = requests.get(f'https://user-to-num-info-zcpe.onrender.com/username/{cl}', timeout=20)
            if r.status_code == 200:
                return r.json()
        except Exception as e:
            print(f'[UN_ZCPE_ERR] {_safe_err(e)}')
        return None

    def _fetch_getchat():
        try:
            r = requests.get(f'https://api.telegram.org/bot{BOT_TOKEN}/getChat', params={'chat_id': f'@{cl}'}, timeout=8)
            if r.status_code == 200:
                return r.json().get('result', {})
        except Exception as e:
            print(f'[UN_GETCHAT_ERR] {_safe_err(e)}')
        return None
    with _cf_un.ThreadPoolExecutor(max_workers=2) as _ex_un:
        _f_api = _ex_un.submit(_fetch_new_api)
        _f_gc = _ex_un.submit(_fetch_getchat)
        d_un = _f_api.result()
        d_gc = _f_gc.result()
        d_abdul_un = None
    if d_un:
        _d_block = d_un.get('data') or {}
        _p1_block = _d_block.get('p1') or {} if isinstance(_d_block, dict) else {}
        _records = _p1_block.get('records') or [] if isinstance(_p1_block, dict) else []
        _is_new_fmt = bool(_records and isinstance(_records, list))
        _id = str(d_un.get('target_id') or d_un.get('telegram_id') or d_un.get('userid') or d_un.get('user_id') or d_un.get('id') or '').strip()
        if not _id or not _id.lstrip('-').isdigit():
            _info_block = d_un.get('info') or {}
            _data_block2 = d_un.get('data') or {}
            if isinstance(_data_block2, dict):
                _id = str(_info_block.get('telegram_id', '') or _data_block2.get('id', '') or _data_block2.get('telegram_id', '') or '').strip()
        if _id and _id.lstrip('-').isdigit():
            tg_id_found = _id
        _ph = ''
        _country = 'India'
        _cc = '+91'
        if _is_new_fmt:
            _rec0 = _records[0] if _records else {}
            _ph_raw = str(_rec0.get('number', '') or '').strip()
            _country = str(_rec0.get('country', 'India') or 'India').strip() or 'India'
            _cc = str(_rec0.get('country_code', '+91') or '+91').strip() or '+91'
            _cc_d = _cc.replace('+', '').strip()
            if _ph_raw and _cc_d and _ph_raw.startswith(_cc_d) and (len(_ph_raw) - len(_cc_d) >= 7):
                _ph = _ph_raw[len(_cc_d):]
            else:
                _ph = _ph_raw
            if not tg_id_found:
                _uid_rec = str(_rec0.get('userid', '') or '').strip()
                if _uid_rec and _uid_rec.lstrip('-').isdigit():
                    tg_id_found = _uid_rec
            print(f'[UN_ZCPE_NEW] cl={cl} tg_id={tg_id_found} phone={_ph}')
        else:
            _info_un2 = d_un.get('info') or {}
            _data_un2 = d_un.get('data') or {} if isinstance(d_un.get('data'), dict) else {}
            _ph_raw = str(d_un.get('number', '') or d_un.get('phone', '') or '').strip()
            if _ph_raw == _id:
                _ph_raw = ''
            _country = str(_info_un2.get('country', '') or d_un.get('country', 'India') or 'India').strip() or 'India'
            _cc = str(_info_un2.get('country_code', '') or d_un.get('country_code', '+91') or '+91').strip() or '+91'
            _cc_d = _cc.replace('+', '').strip()
            if _ph_raw and _cc_d and _ph_raw.startswith(_cc_d) and (len(_ph_raw) - len(_cc_d) >= 7):
                _ph = _ph_raw[len(_cc_d):]
            else:
                _ph = _ph_raw
            print(f'[UN_ZCPE_OLD] cl={cl} tg_id={tg_id_found} phone={_ph}')
        _data_un = d_un.get('data') or {} if isinstance(d_un.get('data'), dict) else {}
        _info_un = d_un.get('info') or {} if isinstance(d_un.get('info'), dict) else {}
        _un_api = str(d_un.get('target_username', '') or _data_un.get('username', '') or cl).replace('@', '').strip()
        _fn = str(_data_un.get('first_name', '') or _info_un.get('first_name', '') or d_un.get('first_name', '') or d_un.get('name', '') or '').strip()
        _ln = str(_data_un.get('last_name', '') or _info_un.get('last_name', '') or d_un.get('last_name', '') or '').strip()
        _bio = str(_data_un.get('bio', '') or _info_un.get('bio', '') or d_un.get('bio', '') or '').strip()
        flat = {'telegram_id': tg_id_found, 'username': _un_api, 'first_name': _fn, 'last_name': _ln, 'bio': _bio, 'is_active': _data_un.get('is_active', ''), 'total_groups': _data_un.get('total_groups', 0), 'admin_groups': _data_un.get('admin_groups', 0), 'total_msg_count': _data_un.get('total_msg_count', 0), 'msg_in_groups_count': _data_un.get('msg_in_groups_count', 0), 'names_count': _data_un.get('names_count', 0), 'usernames_count': _data_un.get('usernames_count', 0), 'first_msg_date': str(_data_un.get('first_msg_date', '') or '').strip(), 'last_msg_date': str(_data_un.get('last_msg_date', '') or '').strip()}
        flat['success'] = True
        if _ph and len(_ph) >= 7:
            flat['phone'] = _ph
            flat['number'] = _ph
            flat['country'] = _country
            flat['country_code'] = _cc
    if d_gc:
        gc_id = str(d_gc.get('id', '') or '').strip()
        if gc_id and (not tg_id_found):
            tg_id_found = gc_id
            flat['telegram_id'] = gc_id
        if d_gc.get('first_name'):
            flat['first_name'] = d_gc['first_name']
        if d_gc.get('last_name'):
            flat['last_name'] = d_gc['last_name']
        if d_gc.get('bio'):
            flat['bio'] = d_gc['bio']
        if not flat.get('username'):
            flat['username'] = d_gc.get('username', cl)
    if d_abdul_un and (not flat.get('phone')):
        _dab = d_abdul_un.get('data') or {}
        _ph_ab = str(_dab.get('number', '') or _dab.get('phone', '') or d_abdul_un.get('number', '') or d_abdul_un.get('phone', '') or '').strip()
        _uid_ab = str(d_abdul_un.get('_resolved_uid', '') or '').strip()
        if _ph_ab and len(_ph_ab) >= 7:
            _cc_ab = str(_dab.get('country_code', '') or d_abdul_un.get('country_code', '+91') or '+91').strip()
            _cc_ab_d = _cc_ab.replace('+', '').strip()
            if _cc_ab_d and _ph_ab.startswith(_cc_ab_d) and (len(_ph_ab) - len(_cc_ab_d) >= 7):
                _ph_ab = _ph_ab[len(_cc_ab_d):]
            flat['phone'] = _ph_ab
            flat['number'] = _ph_ab
            flat['country'] = str(_dab.get('country', '') or d_abdul_un.get('country', 'India') or 'India').strip()
            flat['country_code'] = _cc_ab
            print(f'[UN_ABDUL_PHONE] cl={cl} phone={_ph_ab}')
        if _uid_ab and (not tg_id_found):
            tg_id_found = _uid_ab
            flat['telegram_id'] = _uid_ab
    if tg_id_found:
        pic = _fetch_pfp_by_id(tg_id_found)
    if not flat.get('username'):
        flat['username'] = cl
    if tg_id_found:
        flat['telegram_id'] = tg_id_found
    return (flat, pic)

def _call_uid_api(uid_str):
    """
    UserID API — NEW fast API primary, AbdulStore secondary (parallel)
    URL: https://user-to-num-info-zcpe.onrender.com/userid=<uid>
    Returns: (ud, phone, country, cc, pic)
    """
    import concurrent.futures as _cf_uid

    def _fetch_new_uid_api():
        try:
            r = requests.get(f'https://user-to-num-info-zcpe.onrender.com/userid={uid_str}', timeout=20)
            if r.status_code == 200:
                _d = r.json()
                if _d:
                    return _d
        except Exception as e:
            print(f'[UID_ZCPE_ERR] {_safe_err(e)}')
        for _attempt in range(2):
            try:
                r = requests.get(f'https://tg-id-2-numb-and-tg-info-v3.vercel.app/api/tg?info={uid_str}', timeout=20)
                if r.status_code == 200:
                    _d = r.json()
                    if _d:
                        return _d
                break
            except Exception as e:
                print(f'[UID_TGV3_ERR] attempt={_attempt + 1} {_safe_err(e)}')
                if _attempt == 0:
                    time.sleep(1)
        return None

    def _fetch_abdulstore():
        try:
            r = requests.get('https://store.abdulstoreapi.workers.dev/api/v1', params={'key': 'ak_59eca148e4484ccb50e8575645c32ee1', 'userid': uid_str}, timeout=10)
            if r.status_code == 200:
                return r.json()
        except Exception as e:
            print(f'[UID_ABDUL_ERR] {_safe_err(e)}')
        return None
    with _cf_uid.ThreadPoolExecutor(max_workers=2) as _ex_uid:
        _f_new = _ex_uid.submit(_fetch_new_uid_api)
        _f_abdul = _ex_uid.submit(_fetch_abdulstore)
        d_new = _f_new.result()
        d_abdul = _f_abdul.result()
    phone = ''
    country = 'India'
    cc = '+91'
    ud = {}
    if d_new:
        _status = d_new.get('status', False)
        _p1_block = None
        _top_data = d_new.get('data') or {}
        if isinstance(_top_data, dict):
            _p1_block = _top_data.get('p1') or {}
        _zcpe_recs = _p1_block.get('records', []) if isinstance(_p1_block, dict) else []
        if _zcpe_recs and isinstance(_zcpe_recs, list) and (len(_zcpe_recs) > 0):
            _rec0 = _zcpe_recs[0]
            _ph = str(_rec0.get('number', '') or '').strip()
            country = str(_rec0.get('country', '') or 'India').strip() or 'India'
            cc = str(_rec0.get('country_code', '') or '+91').strip() or '+91'
            if _ph and _ph != uid_str and (len(_ph) >= 7):
                phone = _ph
                _cc_d = cc.replace('+', '').strip()
                if _cc_d and phone.startswith(_cc_d) and (len(phone) - len(_cc_d) >= 7):
                    phone = phone[len(_cc_d):]
            ud = {'telegram_id': uid_str, 'success': True}
            if phone:
                ud['number'] = phone
                ud['phone'] = phone
            if country:
                ud['country'] = country
            if cc:
                ud['country_code'] = cc
            print(f'[UID_ZCPE] uid={uid_str} phone={phone} country={country} cc={cc}')
        else:
            _data = _top_data if isinstance(_top_data, dict) else {}
            _info = d_new.get('info') or {}
            _ph = str(d_new.get('number', '') or '').strip()
            if _ph and _ph != uid_str and (len(_ph) >= 7):
                phone = _ph
                country = str(_info.get('country', '') or 'India').strip() or 'India'
                cc = str(_info.get('country_code', '') or '+91').strip() or '+91'
                _cc_d = cc.replace('+', '').strip()
                if _cc_d and phone.startswith(_cc_d) and (len(phone) - len(_cc_d) >= 7):
                    phone = phone[len(_cc_d):]
            ud = {'telegram_id': uid_str, 'username': str(d_new.get('target_username', '') or _data.get('username', '') or '').strip(), 'first_name': str(_data.get('first_name', '') or d_new.get('first_name', '') or '').strip(), 'last_name': str(_data.get('last_name', '') or d_new.get('last_name', '') or '').strip(), 'bio': str(_data.get('bio', '') or d_new.get('bio', '') or '').strip(), 'is_active': _data.get('is_active', ''), 'total_groups': _data.get('total_groups', 0), 'admin_groups': _data.get('admin_groups', 0), 'total_msg_count': _data.get('total_msg_count', 0), 'msg_in_groups_count': _data.get('msg_in_groups_count', 0), 'names_count': _data.get('names_count', 0), 'usernames_count': _data.get('usernames_count', 0), 'first_msg_date': str(_data.get('first_msg_date', '') or '').strip(), 'last_msg_date': str(_data.get('last_msg_date', '') or '').strip(), 'success': True}
            if phone:
                ud['number'] = phone
                ud['phone'] = phone
            if country:
                ud['country'] = country
            if cc:
                ud['country_code'] = cc
            print(f"[UID_TGV3] uid={uid_str} phone={phone} active={ud.get('is_active')} groups={ud.get('total_groups')}")
    if d_abdul and (not phone):
        d1_inner = d_abdul.get('data') or {}
        _ph2 = str(d1_inner.get('number', '') or d1_inner.get('phone', '') or d_abdul.get('number', '') or d_abdul.get('phone', '') or '').strip()
        if _ph2 and _ph2 != uid_str and (len(_ph2) >= 7):
            phone = _ph2
            country = d1_inner.get('country', '') or d_abdul.get('country', 'India') or 'India'
            cc = d1_inner.get('country_code', '') or d_abdul.get('country_code', '+91') or '+91'
            if not ud:
                ud = dict(d_abdul)
                ud['success'] = True
            ud['number'] = phone
            ud['phone'] = phone
            print(f'[UID_ABDUL] uid={uid_str} phone={phone}')
    pic = _fetch_pfp_by_id(uid_str)
    if ud:
        return (ud, phone or 'N/A', country, cc, pic)
    tg_fb = _fetch_tg_user_direct(uid_str)
    pic_fb = pic or _fetch_pfp_by_id(uid_str)
    if tg_fb:
        ud_fb = {'telegram_id': uid_str, 'first_name': tg_fb.get('first_name', ''), 'last_name': tg_fb.get('last_name', ''), 'username': tg_fb.get('username', ''), 'bio': tg_fb.get('bio', ''), 'success': True}
        return (ud_fb, 'N/A', 'India', '+91', pic_fb or tg_fb.get('pfp_url'))
    return ({}, 'N/A', 'India', '+91', pic)
MERGE_KEYS = ['username', 'bio', 'first_name', 'last_name', 'is_active', 'members', 'total_groups', 'admin_groups', 'total_messages', 'group_messages', 'names_used', 'usernames_used', 'first_message', 'last_message', 'premium', 'verified', 'last_seen', 'telegram_id']

def _build_ud(uid_data, flat):
    """Merge userid API data + username API flat data — username API wins for detail fields"""
    ud = dict(uid_data)
    _str_keys = ('bio', 'username', 'first_name', 'last_name', 'country', 'country_code', 'phone', 'number')
    for key in MERGE_KEYS:
        val = flat.get(key)
        if key in _str_keys:
            if val not in (None, '') and isinstance(val, str):
                ud[key] = val
        elif val not in (None, '', 0):
            ud[key] = val
        elif key not in ud or ud.get(key) in (None, '', 0):
            if val is not None:
                ud[key] = val
    return ud

def api_userid(uid_t):
    """
    Fetch user info using 3 sources concurrently:
    1. Telegram Bot API (getChat + getUserProfilePhotos) — PRIMARY, most reliable
    2. userid API (sh4dow)
    3. username API (username-to-info)
    Merge all, best data wins.
    """
    import concurrent.futures as _cfu2
    import time as _t_uid
    ci = re.sub('\\D', '', str(uid_t))
    _t_uid_start = _t_uid.time()
    try:
        with _cfu2.ThreadPoolExecutor(max_workers=3) as ex:
            f_tg = ex.submit(_fetch_tg_user_direct, ci)
            f_uid = ex.submit(_call_uid_api, ci)
            f_unid = ex.submit(_call_un_api_by_id, ci)
            tg = f_tg.result()
            uid_data, phone, country, cc, pic1 = f_uid.result()
            flat2, pic2 = f_unid.result()
        un_from_tg = (tg.get('username') or uid_data.get('username') or flat2.get('username') or '').replace('@', '').strip()
        flat = flat2
        if un_from_tg and (not flat2):
            flat, pic2 = _call_un_api(un_from_tg)
        ud = _build_ud(uid_data, flat)
        if tg.get('first_name'):
            ud['first_name'] = tg['first_name']
        if tg.get('last_name'):
            ud['last_name'] = tg['last_name']
        if tg.get('username'):
            ud['username'] = tg['username']
        if tg.get('bio'):
            ud['bio'] = tg['bio']
        ud['telegram_id'] = ci
        for key in MERGE_KEYS:
            if key not in ud or ud.get(key) in (None, '', 0):
                val = flat.get(key)
                if val not in (None, '', 0):
                    ud[key] = val
        if not phone or phone == 'N/A':
            phone = flat.get('phone') or flat.get('number') or 'N/A'
        if country == 'India' and flat.get('country'):
            country = flat.get('country', 'India')
        if cc == '+91' and flat.get('country_code'):
            cc = flat.get('country_code', '+91')
        pic_media = f'http://username-to-info-rwsw.onrender.com/media/{ci}.png'
        pic = tg.get('pfp_url') or pic2 or pic_media or pic1
        _rt = f'{int((_t_uid.time() - _t_uid_start) * 1000)}ms'
        return {'success': True, 'phone': phone, 'target_id': ci, 'telegram_id': ci, 'country': country, 'country_code': cc, 'data': ud, 'profile_pic': pic, 'response_time': _rt}
    except Exception as e:
        print(f'[API_USERID] {_safe_err(e)}')
    tg = _fetch_tg_user_direct(ci)
    ud = {'telegram_id': ci}
    if tg.get('first_name'):
        ud['first_name'] = tg['first_name']
    if tg.get('last_name'):
        ud['last_name'] = tg['last_name']
    if tg.get('username'):
        ud['username'] = tg['username']
    if tg.get('bio'):
        ud['bio'] = tg['bio']
    pic = tg.get('pfp_url') or f'http://username-to-info-rwsw.onrender.com/media/{ci}.png'
    return {'success': True, 'phone': 'N/A', 'target_id': ci, 'telegram_id': ci, 'country': '—', 'country_code': '', 'data': ud, 'profile_pic': pic, 'response_time': 'N/A'}

def _call_un_api_by_id(uid_str):
    """Try new tg-id-2-numb / f2 API first, then AbdulStore — get phone + activity by user ID"""

    def _parse_uid_flat(d, uid_str):
        _data = d.get('data') or {}
        _info = d.get('info') or {}
        phone = str(d.get('number', '') or d.get('phone', '') or '').strip()
        _ph_valid = phone and phone != uid_str and (len(phone) >= 7)
        _has_data = bool(_data or d.get('status') or d.get('first_name') or d.get('telegram_id') or d.get('target_id'))
        if not _ph_valid and (not _has_data):
            return None
        flat = {'telegram_id': uid_str, 'first_name': str(_data.get('first_name', '') or d.get('first_name', '') or '').strip(), 'last_name': str(_data.get('last_name', '') or d.get('last_name', '') or '').strip(), 'is_active': _data.get('is_active', ''), 'total_groups': _data.get('total_groups', 0), 'admin_groups': _data.get('admin_groups', 0), 'total_msg_count': _data.get('total_msg_count', 0), 'msg_in_groups_count': _data.get('msg_in_groups_count', 0), 'names_count': _data.get('names_count', 0), 'usernames_count': _data.get('usernames_count', 0), 'first_msg_date': str(_data.get('first_msg_date', '') or '').strip(), 'last_msg_date': str(_data.get('last_msg_date', '') or '').strip()}
        if _ph_valid:
            flat['phone'] = phone
            flat['number'] = phone
            flat['country'] = str(_info.get('country', '') or d.get('country', 'India') or 'India').strip()
            flat['country_code'] = str(_info.get('country_code', '') or d.get('country_code', '+91') or '+91').strip()
        return flat
    try:
        r = requests.get(f'https://tg-id-2-numb-and-tg-info-v3.vercel.app/api/tg?info={uid_str}', timeout=12)
        if r.status_code == 200:
            d = r.json()
            flat = _parse_uid_flat(d, uid_str)
            if flat:
                pic = _fetch_pfp_by_id(uid_str)
                return (flat, pic)
    except Exception as e:
        print(f'[UN_BY_ID_TGV3_ERR] {_safe_err(e)}')
    try:
        r = requests.get(f'https://user-to-num-info-zcpe.onrender.com/userid={uid_str}', timeout=10)
        if r.status_code == 200:
            d = r.json()
            flat = _parse_uid_flat(d, uid_str)
            if flat:
                pic = _fetch_pfp_by_id(uid_str)
                return (flat, pic)
    except Exception as e:
        print(f'[UN_BY_ID_NEWAPI_ERR] {_safe_err(e)}')
    try:
        r = requests.get('https://store.abdulstoreapi.workers.dev/api/v1', params={'key': 'ak_59eca148e4484ccb50e8575645c32ee1', 'userid': uid_str}, timeout=10)
        if r.status_code == 200:
            d = r.json()
            if d and (d.get('success') or d.get('number') or d.get('phone') or d.get('name')):
                phone = str(d.get('number', '') or d.get('phone', '') or '').strip()
                flat = {'telegram_id': uid_str, 'phone': phone if phone != uid_str else '', 'number': phone if phone != uid_str else '', 'country': d.get('country', 'India') or 'India', 'country_code': d.get('country_code', '+91') or '+91'}
                pic = _fetch_pfp_by_id(uid_str)
                return (flat, pic)
    except Exception as e:
        print(f'[UN_BY_ID_ABDUL_ERR] {_safe_err(e)}')
    return ({}, None)

def _fetch_tg_user_direct(uid_str):
    """
    Fetch user info DIRECTLY from Telegram Bot API.
    Returns dict with: first_name, last_name, username, bio, pfp_url
    This is the most reliable source — works even when 3rd party APIs fail.
    """
    result = {}
    _raw = str(uid_str).strip()
    if _raw.startswith('@') or not _raw.lstrip('-').isdigit():
        uid_str = '@' + _raw.replace('@', '').strip()
        _for_photo = None
    else:
        uid_str = re.sub('\\D', '', _raw)
        _for_photo = uid_str
    try:
        r = requests.get(f'https://api.telegram.org/bot{BOT_TOKEN}/getChat', params={'chat_id': uid_str}, timeout=10)
        if r.status_code == 200:
            d = r.json().get('result', {})
            result['first_name'] = d.get('first_name', '') or ''
            result['last_name'] = d.get('last_name', '') or ''
            result['username'] = d.get('username', '') or ''
            result['bio'] = d.get('bio', '') or ''
            result['type'] = d.get('type', '')
            result['tg_id'] = str(d.get('id', uid_str))
            if _for_photo is None and d.get('id'):
                _for_photo = str(d['id'])
    except Exception as e:
        print(f'[TG_DIRECT getChat] {_safe_err(e)}')
    if _for_photo:
        try:
            r2 = requests.get(f'https://api.telegram.org/bot{BOT_TOKEN}/getUserProfilePhotos', params={'user_id': _for_photo, 'limit': 1}, timeout=10)
            if r2.status_code == 200:
                photos = r2.json().get('result', {}).get('photos', [])
                if photos and photos[0]:
                    file_id = photos[0][-1].get('file_id', '')
                    if file_id:
                        r3 = requests.get(f'https://api.telegram.org/bot{BOT_TOKEN}/getFile', params={'file_id': file_id}, timeout=10)
                        if r3.status_code == 200:
                            fpath = r3.json().get('result', {}).get('file_path', '')
                            if fpath:
                                result['pfp_url'] = f'https://api.telegram.org/file/bot{BOT_TOKEN}/{fpath}'
        except Exception as e:
            print(f'[TG_DIRECT photo] {_safe_err(e)}')
    return result

def api_full_user(query, _timeout=30):
    """
    UNIFIED: query = @username ya numeric ID
    Teeno sources se maximum data nikalo aur merge karo.
    Username button, TG ID button, Select User — teeno yahi use karein.
    Returns same format as api_userid.
    """
    import concurrent.futures as _cff
    import time as _t_full
    query = str(query).strip()
    is_uid = query.lstrip('-').isdigit()
    cl = query.replace('@', '').strip()
    _t_start = _t_full.time()
    _luffy_base = None
    try:
        _tg_q = cl if not is_uid else cl
        if not is_uid and (not _tg_q.startswith('@')):
            _tg_q = '@' + _tg_q
        _not_coder_url = f'https://𝙽𝚘𝚝 𝙲𝚘𝚍𝚎𝚛-info-x-bot.onrender.com/key=𝙽𝚘𝚝 𝙲𝚘𝚍𝚎𝚛67&tg={_tg_q}'
        _fr = requests.get(_not_coder_url, timeout=min(25, _timeout))
        if _fr.status_code == 200:
            _fd = _fr.json()
            if isinstance(_fd, dict) and (_fd.get('number') or _fd.get('tg_id')):
                _phone = str(_fd.get('number') or '').strip()
                _tid = str(_fd.get('tg_id') or (cl if is_uid else '')).strip()
                _uname = str(_fd.get('username') or ('' if is_uid else cl)).replace('@', '')
                _rt = _fd.get('response_time_ms')
                try:
                    _rt_s = f'{float(_rt) / 1000:.2f}s' if _rt is not None else f'{int((_t_full.time() - _t_start) * 1000)}ms'
                except Exception:
                    _rt_s = f'{int((_t_full.time() - _t_start) * 1000)}ms'
                if _phone:
                    return {'success': True, 'phone': _phone, 'telegram_id': _tid, 'target_id': _tid, 'target_username': _uname, 'country': _fd.get('country') or 'INDIA', 'country_code': _fd.get('country_code') or '+91', 'data': {'telegram_id': _tid, 'username': _uname, 'phone': _phone, 'number': _phone}, 'response_time': _rt_s, '_api_source': '𝙽𝚘𝚝 𝙲𝚘𝚍𝚎𝚛_tg'}
                _luffy_base = {'success': True, 'phone': 'N/A', 'telegram_id': _tid, 'data': {'telegram_id': _tid, 'username': _uname}, '_api_source': '𝙽𝚘𝚝 𝙲𝚘𝚍𝚎𝚛_tg'}
    except Exception as _fe:
        print(f'[𝙽𝚘𝚝 𝙲𝚘𝚍𝚎𝚛_TG] {_fe}')
    try:
        if is_uid:
            _lr = _luffy_get({'tgid': cl}, timeout=min(20, _timeout))
        else:
            _lr = _luffy_get({'tg': cl}, timeout=min(20, _timeout))
        _lt = _luffy_norm_tg(_lr, query)
        if _lt and _lt.get('success'):
            _lt['response_time'] = f'{int((_t_full.time() - _t_start) * 1000)}ms'
            _ph = str(_lt.get('phone') or '').strip()
            if _ph and _ph not in ('N/A', 'None', ''):
                return _lt
            if not _luffy_base:
                _luffy_base = _lt
    except Exception as _lte:
        print(f'[LUFFY_TG] {_lte}')

    def _run_tg(q):
        try:
            return _fetch_tg_user_direct(re.sub('\\D', '', q) if q.lstrip('-').isdigit() else q)
        except:
            return {}

    def _run_uid(q):
        if q.lstrip('-').isdigit():
            return _call_uid_api(q)
        try:
            _uname_clean = q.replace('@', '').strip()
            _gc = requests.get(f'https://api.telegram.org/bot{BOT_TOKEN}/getChat', params={'chat_id': f'@{_uname_clean}'}, timeout=10)
            if _gc.status_code == 200:
                _gc_id = str(_gc.json().get('result', {}).get('id', '') or '').strip()
                if _gc_id and _gc_id.lstrip('-').isdigit():
                    return _call_uid_api(_gc_id)
        except:
            pass
        return ({}, 'N/A', 'India', '+91', None)

    def _run_un(q):
        if q.lstrip('-').isdigit():
            r1, p1 = _call_un_api_by_id(q)
            if r1:
                return (r1, p1)
            return ({}, None)
        return _call_un_api(q)
    try:
        with _cff.ThreadPoolExecutor(max_workers=3) as ex:
            ft = ex.submit(_run_tg, query)
            fu = ex.submit(_run_uid, query)
            fn = ex.submit(_run_un, cl)
            tg = ft.result()
            uid_res = fu.result()
            un_res = fn.result()
        if isinstance(uid_res, tuple) and len(uid_res) == 5:
            uid_data, phone, country, cc, pic1 = uid_res
        else:
            uid_data = {}
            phone = 'N/A'
            country = 'India'
            cc = '+91'
            pic1 = None
        flat, pic2 = un_res if isinstance(un_res, tuple) and len(un_res) == 2 else ({}, None)
        flat = flat or {}
        tg_id = tg.get('tg_id') or str(flat.get('telegram_id') or flat.get('id') or '') or uid_data.get('telegram_id', '') or (re.sub('\\D', '', query) if is_uid else '')
        un_from_tg = (tg.get('username') or flat.get('username') or uid_data.get('username') or '').replace('@', '').strip()
        if un_from_tg and (not flat) and (not is_uid):
            try:
                flat, pic2 = _call_un_api(un_from_tg)
            except:
                pass
        flat = flat or {}
        ud = _build_ud(uid_data, flat)
        if tg.get('first_name'):
            ud['first_name'] = tg['first_name']
        if tg.get('last_name'):
            ud['last_name'] = tg['last_name']
        if tg.get('username'):
            ud['username'] = tg['username']
        if tg.get('bio'):
            ud['bio'] = tg['bio']
        if tg_id:
            ud['telegram_id'] = tg_id
        for key in MERGE_KEYS:
            if key not in ud or ud.get(key) in (None, '', 0):
                val = flat.get(key)
                if val not in (None, '', 0):
                    ud[key] = val
        if not phone or phone == 'N/A':
            phone = flat.get('phone') or flat.get('number') or 'N/A'
        if country == 'India' and flat.get('country') and (flat['country'] != 'India'):
            country = flat['country']
        if cc == '+91' and flat.get('country_code') and (flat['country_code'] != '+91'):
            cc = flat['country_code']
        if phone and phone != 'N/A' and cc:
            _cc_d2 = cc.replace('+', '').strip()
            if _cc_d2 and phone.startswith(_cc_d2) and (len(phone) - len(_cc_d2) >= 7):
                phone = phone[len(_cc_d2):]
        pic_media = f'http://username-to-info-rwsw.onrender.com/media/{tg_id}.png' if tg_id else None
        pic = tg.get('pfp_url') or pic2 or pic_media or pic1
        if not pic and tg_id:
            pic = _fetch_pfp_by_id(tg_id)
        _rt_full = f'{int((_t_full.time() - _t_start) * 1000)}ms'
        try:
            if (not phone or phone in ('N/A', '', None)) and _luffy_base:
                _lp = str(_luffy_base.get('phone') or '').strip()
                if _lp and _lp not in ('N/A', ''):
                    phone = _lp
                    ud['phone'] = _lp
                    ud['number'] = _lp
            if not tg_id and _luffy_base and _luffy_base.get('telegram_id'):
                tg_id = str(_luffy_base.get('telegram_id'))
                ud['telegram_id'] = tg_id
        except Exception:
            pass
        return {'success': True, 'phone': phone, 'telegram_id': tg_id, 'target_id': tg_id, 'target_username': un_from_tg or cl, 'country': country, 'country_code': cc, 'profile_pic': pic, 'profile_picture': pic, 'data': ud, 'response_time': _rt_full}
    except Exception as e:
        print(f'[API_FULL_USER] {_safe_err(e)}')
        tg = _fetch_tg_user_direct(re.sub('\\D', '', query) if is_uid else query)
        ud = {'telegram_id': tg.get('tg_id', query)}
        for k in ('first_name', 'last_name', 'username', 'bio'):
            if tg.get(k):
                ud[k] = tg[k]
        pic = tg.get('pfp_url')
        return {'success': bool(tg), 'phone': 'N/A', 'telegram_id': query, 'target_id': query, 'target_username': cl, 'country': '—', 'country_code': '', 'profile_pic': pic, 'data': ud, 'response_time': 'N/A'}

def do_ff_like_send(chat_id, msg_id, uid, region, user_id, fname):
    """Send likes using 6 APIs in parallel — simran API new primary"""
    import concurrent.futures as _cfl
    region_display = REGION_NAMES.get(region.lower(), region.upper())
    _anim_stop = [False]

    def _animate_pbar():
        steps = [(5, 0.2), (20, 0.3), (40, 0.3), (60, 0.3), (80, 0.3), (93, 0.2)]
        for pct, delay in steps:
            if _anim_stop[0]:
                break
            try:
                bot.edit_message_text(f'<blockquote>{pbar(pct)}\n⚡ ꜱᴇɴᴅɪɴɢ ʟɪᴋᴇꜱ...</blockquote>', chat_id, msg_id, parse_mode='HTML')
            except:
                pass
            time.sleep(delay)
    anim_thread = threading.Thread(target=_animate_pbar, daemon=True)
    anim_thread.start()

    def try_api0():
        try:
            r = requests.get(LIKE_API_0, params={'uid': uid, 'server_name': region.lower()}, timeout=25)
            if r.status_code == 200:
                return r.json()
        except:
            pass
        return None

    def try_api1():
        try:
            r = requests.get(LIKE_API_1, params={'uid': uid, 'server_name': region.lower()}, headers={'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json'}, timeout=25)
            if r.status_code == 200:
                return r.json()
        except:
            pass
        return None

    def try_api2():
        try:
            r = requests.get(LIKE_API_2, params={'uid': uid, 'server_name': region.lower()}, timeout=25)
            if r.status_code == 200:
                return r.json()
        except:
            pass
        return None

    def try_api3():
        try:
            r = requests.get(LIKE_API_3, params={'uid': uid, 'server_name': region.upper()}, headers={'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json'}, timeout=25)
            if r.status_code == 200:
                return r.json()
        except:
            pass
        return None

    def try_api4():
        try:
            r = requests.get(LIKE_API_4, params={'uid': uid, 'region': region, 'key': 'UDIT'}, timeout=25)
            if r.status_code == 200:
                return r.json()
        except:
            pass
        return None

    def try_api5():
        try:
            r = requests.get(LIKE_API_5, params={'uid': uid, 'server_name': region.lower()}, timeout=25)
            if r.status_code == 200:
                return r.json()
        except:
            pass
        return None
    with _cfl.ThreadPoolExecutor(max_workers=6) as ex:
        f0 = ex.submit(try_api0)
        fa = ex.submit(try_api1)
        fb = ex.submit(try_api2)
        fc = ex.submit(try_api3)
        fd = ex.submit(try_api4)
        fe = ex.submit(try_api5)
        d0 = f0.result()
        d1 = fa.result()
        d2 = fb.result()
        d3 = fc.result()
        d4 = fd.result()
        d5 = fe.result()
    _anim_stop[0] = True
    anim_thread.join(timeout=1)
    now_str = _now_ist()
    total_given = 0
    results_txt = ''
    already_liked = False
    api_results = [('1', d1), ('2', d2), ('3', d3), ('4', d4), ('5', d5), ('6', d0)]
    for i, (label, data) in enumerate(api_results):
        if not data:
            continue
        if 'error' in data:
            results_txt += f"\n◆ 𝐀𝐏𝐈 {label} : ❌ {data.get('error', '')}"
            continue
        status = data.get('status', 0)
        msg_txt = str(data.get('message', data.get('msg', ''))).lower()
        if 'already' in msg_txt or 'max' in msg_txt or 'limit' in msg_txt:
            already_liked = True
            results_txt += f"\n{('◆' if int(label) % 2 != 0 else '◇')} 𝐀𝐏𝐈 {label} : ⚠️ Already Liked"
        elif status in [1, 2, 3]:
            lb = data.get('LikesbeforeCommand', data.get('likes_before', 0))
            la = data.get('LikesafterCommand', data.get('likes_after', 0))
            lg = data.get('LikesGivenByAPI', data.get('likes_given', 1))
            total_given += int(lg or 0)
            results_txt += f"\n{('◆' if int(label) % 2 != 0 else '◇')} 𝐀𝐏𝐈 {label} : {lb} → {la} (+{lg})"
        else:
            results_txt += f"\n{('◆' if int(label) % 2 != 0 else '◇')} 𝐀𝐏𝐈 {label} : ⚠️ {data.get('message', data.get('msg', 'Failed'))}"
    if not results_txt:
        results_txt = '\n◆  ᴋᴏɪ ʙʜɪ API ʀᴇꜱᴩᴏɴᴅ ɴᴀʜɪ ᴋɪ'
    if total_given > 0:
        _like_update_cooldown(user_id, uid, region)
        _like_update_ratelimit(user_id)
    remain = _like_remaining_daily(user_id)
    next_t = (datetime.now() + timedelta(hours=LIKE_COOLDOWN_HOURS)).strftime('%I:%M %p')
    _TE = lambda eid, fb: ''
    _LOOP10 = _TE('5465270065102334742', '') * 10
    if already_liked and total_given == 0:
        status_icon = f"{_TE('6179105681375760937', '')} ᴀʟʀᴇᴀᴅʏ ʟɪᴋᴇᴅ"
    elif total_given > 0:
        status_icon = f"{_TE('6179105681375760937', '')} <b>LIKES SENT!</b> {_TE('5436040291507247633', '')}"
    else:
        status_icon = f'❌ <b>LIKE FAILED</b>'
    api_lines_premium = ''
    api_lines_plain = ''
    player_name = ''
    try:
        pinfo = api_ff_like(uid)
        if pinfo:
            player_name = pinfo.get('nickname', '') or ''
    except:
        pass
    for i, (label, data) in enumerate(api_results):
        if not data:
            continue
        _gm = _TE('5350803719170564382', '')
        _crown = _TE('6158882647473920838', '')
        if 'error' in data:
            api_lines_premium += f"│ {_gm} ᴀᴩɪ {label}: ❌ {data.get('error', '')}\n"
            continue
        status = data.get('status', 0)
        msg_txt = str(data.get('message', data.get('msg', ''))).lower()
        if 'already' in msg_txt or 'max' in msg_txt or 'limit' in msg_txt:
            api_lines_premium += f'│ {_gm} ᴀᴩɪ {label}: ⚠️ Already Liked\n'
        elif status in [1, 2, 3]:
            lb2 = data.get('LikesbeforeCommand', data.get('likes_before', 0))
            la2 = data.get('LikesafterCommand', data.get('likes_after', 0))
            lg2 = data.get('LikesGivenByAPI', data.get('likes_given', 1))
            api_lines_premium += f'│ {_gm} ᴀᴩɪ {label}: {_crown} {lb2} → {la2} (+{lg2})\n'
        else:
            api_lines_premium += f"│ {_gm} ᴀᴩɪ {label}: ⚠️ {data.get('message', data.get('msg', 'Failed'))}\n"
    _pe_uid = _TE('5888781182249738113', '')
    _pe_usr = _TE('6035084557378654059', '')
    _pe_flag = _TE('5447419223242449630', '')
    _pe_globe = _TE('6114021507908767611', '')
    _region_pe = f"{_pe_flag} {region_display.replace('', '').strip()}" if 'India' in region_display or 'IND' in region_display.upper() else f'{_pe_globe} {region_display}'
    txt = f"<blockquote>{_LOOP10}\n   {_TE('6158973086600273462', '')} ꜰꜰ ʟɪᴋᴇ ʀᴇꜱᴜʟᴛ\n{_LOOP10}\n\n{status_icon}\n\n╭─── {_pe_usr} ᴩʟᴀʏᴇʀ ───╮\n{('│  ɴᴀᴍᴇ   : ' + player_name + chr(10) if player_name else '')}│ {_pe_uid} UID    : {uid}\n│ {_pe_globe} ʀᴇɢɪᴏɴ : {_region_pe}\n╰──────────────────╯\n\n╭─── 📊 ᴀᴩɪ ʀᴇꜱᴜʟᴛꜱ ───╮\n{api_lines_premium}╰──────────────────╯\n\n{_LOOP10}\n   {_TE('5436040291507247633', '')}  TOTAL : +{total_given} LIKES ! {_TE('5469785308386041323', '')}\n{_LOOP10}\n\n{_TE('5413704112220949842', '')} ɴᴇxᴛ (ᴛʜɪꜱ ᴜɪᴅ): {next_t}\n{_TE('5431577498364158238', '')} ᴅᴀɪʟʏ ʟᴇꜰᴛ: {remain}/{LIKE_DAILY_MAX}\n{_TE('5472146462362048818', '')} ᴅɪꜰꜰᴇʀᴇɴᴛ ᴜɪᴅꜱ = ɴᴏ ᴄᴏᴏʟᴅᴏᴡɴ!\n\n{_TE('6242308461598610637', '')} {now_str}\n{_LOOP10}\n{_TE('6147464060305676048', '')} @notCoder2006 {_TE('6147565374289220368', '')}\n{_LOOP10}</blockquote>"
    try:
        bot.edit_message_text(txt, chat_id, msg_id, parse_mode='HTML')
    except:
        bot.send_message(chat_id, txt, parse_mode='HTML')
FLIX_BOMBER_API = 'https://bombar-api-2.vercel.app/all'
FLIX_BOMBER_STOP = 'https://flix-bombar.onrender.com/stop'
RLX_BOMBER_API = 'https://rlxbomber.vercel.app/api/attack'
RLX_BOMBER_KEY = 'rlxcoder'
RLX_BOMBER_API2 = 'https://rlxbomber.vercel.app/api/attack'
RLX_BOMBER_KEY2 = 'rlxcoder'

def _s(t):
    """Convert to small caps stylish text"""
    M = {'A': 'ᴀ', 'B': 'ʙ', 'C': 'ᴄ', 'D': 'ᴅ', 'E': 'ᴇ', 'F': 'ꜰ', 'G': 'ɢ', 'H': 'ʜ', 'I': 'ɪ', 'J': 'ᴊ', 'K': 'ᴋ', 'L': 'ʟ', 'M': 'ᴍ', 'N': 'ɴ', 'O': 'ᴏ', 'P': 'ᴘ', 'Q': 'Q', 'R': 'ʀ', 'S': 'ꜱ', 'T': 'ᴛ', 'U': 'ᴜ', 'V': 'ᴠ', 'W': 'ᴡ', 'X': 'x', 'Y': 'ʏ', 'Z': 'ᴢ'}
    return ''.join((M.get(c.upper(), c) for c in str(t)))

def _fmt_tg_user_short(res, query_display, now_str, credits_left=None):
    return _fmt_tg_user(res, '', 'USERNAME INFO', query_display, now_str, credits_left)

def _fmt_tg_user(res, title_icon, title_text, query_display, now_str, credits_left=None):
    """TG → Number card — new premium design"""

    def _pe(*args, **kwargs): return ""
    _L = _pe('5465270065102334742', '') * 10
    _plane = _pe('5246931953751443616', '')
    _chat = _pe('6030776052345737530', '')
    _phone = _pe('6046178745667031983', '')
    _rocket = _pe('6203911118964924015', '')
    _brick = _pe('5326049357332513437', '')
    _bot = _pe('5355051922862653659', '')
    _star = _pe('6118385795976930086', '')
    try:
        bn = _get_bot_username()
    except:
        bn = 'bot'
    ud = res.get('data') or {} if res else {}
    tg_id = str(ud.get('telegram_id') or (res or {}).get('telegram_id') or (res or {}).get('target_id') or '').strip()
    if not tg_id:
        q = str(query_display or '').replace('@', '').strip()
        if q.lstrip('-').isdigit():
            tg_id = q
    phone = str((res or {}).get('phone') or (res or {}).get('number') or ud.get('phone') or ud.get('number') or '').strip()
    if phone in ('N/A', 'None', 'null', '—', '-'):
        phone = ''
    if phone and tg_id and (phone == tg_id):
        phone = ''
    resp = str((res or {}).get('response_time') or '').strip()
    if resp.endswith('ms'):
        try:
            ms = float(resp.replace('ms', '').strip())
            resp = f'{ms / 1000:.2f}s'
        except:
            pass
    if not resp or resp in ('N/A', '—'):
        resp = '—'
    if phone:
        phone_block = f'{_phone} Tᴇʟᴇᴩʜᴏɴᴇ (1):\n╰ <code>{phone}</code>'
    else:
        phone_block = f'{_phone} Tᴇʟᴇᴩʜᴏɴᴇ (0):\n╰ Not Found'
    cr_disp = credits_left if credits_left is not None else '—'
    txt = f"<blockquote>{_plane} Tᴇʟᴇɢʀᴀᴍ\n╰ {_chat}ID: <code>{tg_id or query_display or '—'}</code>\n\n{phone_block}\n\n{_rocket}ʀᴇꜱᴩᴏɴꜱᴇ ᴛɪᴍᴇ:- {resp}\n{_brick}ᴄʀᴇᴅɪᴛꜱ ʟᴇꜰᴛ:- {cr_disp}\n{_L}\n{_bot}Pᴏᴡᴇʀᴇᴅ Bʏ: @{bn} {_star}\n{_L}</blockquote>"
    return (txt, None)

def fmt_userid(res, tid, searcher):
    now = _now_ist()
    return _fmt_tg_user(res, '', 'TG ID INFO', str(tid), now)

def _split_person_name(full_name):
    """Name ko first_name, middle_name, last_name mein split karo"""
    clean = _clean_na(full_name)
    if not clean:
        return (None, None, None, None)
    parts = clean.split()
    if len(parts) == 1:
        return (clean, parts[0], None, None)
    if len(parts) == 2:
        return (clean, parts[0], None, parts[1])
    return (clean, parts[0], parts[1], ' '.join(parts[2:]))


def fmt_number_page(d, num, page=1, per_page=2, uid=None, elapsed=None):
    """Returns (text, total_pages, has_prev, has_next) in JSON code-block format with COPY CODE support"""
    try:
        bn = _get_bot_username()
    except Exception:
        bn = '𝙽𝚘𝚝 𝙲𝚘𝚍𝚎𝚛'

    req_name = 'User'
    cr_left = '—'
    if uid is not None:
        try:
            u_row = get_user(uid)
            if u_row and u_row[2]:
                req_name = str(u_row[2])
        except Exception:
            pass
        try:
            cr_left = '∞' if is_admin(uid) else get_credits(uid)
        except Exception:
            cr_left = '—'

    if elapsed is None and uid is not None and (uid in _num_cache):
        elapsed = _num_cache[uid].get('elapsed')
    try:
        t_str = f'{float(elapsed):.2f}s' if elapsed is not None else '—'
    except Exception:
        t_str = '—'

    req_link = f"<a href='tg://user?id={uid}'>{_html.escape(req_name)}</a>" if uid else _html.escape(req_name)
    header = (
        f"<b>Number to Info</b>\n"
        f"<b>Requested by:</b> {req_link}\n"
        f"<b>Query:</b> <code>{_html.escape(str(num))}</code>\n\n"
    )
    footer = (
        f"\n🚀 <b>Response Time:</b> <code>{t_str}</code>"
        f"\n🪙 <b>Credits Left:</b> <code>{cr_left}</code>"
        f"\n🤖 <b>Powered By:</b> @{bn} ⭐"
    )

    if not d or not d.get('success'):
        err_json = json.dumps({
            'status': 'FAILED',
            'type': 'Number to Info',
            'total_records': 0,
            'result': [],
            'developer': f'@{bn}',
        }, indent=2, ensure_ascii=False)
        txt = f"{header}<pre><code class=\"language-json\">{_html.escape(err_json)}</code></pre>{footer}"
        return (txt, 1, False, False)

    recs = []
    if d.get('_api_source') == 'simran_num' or isinstance(d.get('data'), list):
        recs = d.get('data') or []
        if not isinstance(recs, list):
            recs = []
    elif d.get('_api_source') == 'rbot':
        recs = d.get('results') or d.get('data') or []
        if not isinstance(recs, list):
            recs = []
    else:
        recs = [d[k] for k in sorted(d.keys()) if k.isdigit() and d[k]]

    norm = []
    for rec in recs:
        if not isinstance(rec, dict):
            continue
        full_nm, first_nm, mid_nm, last_nm = _split_person_name(rec.get('name'))
        fname_val = _clean_na(rec.get('fname') or rec.get('father_name')) or None
        mob_val = _clean_na(rec.get('mobile') or rec.get('number')) or str(num)
        alt_val = _clean_na(rec.get('alt') or rec.get('alt_number') or rec.get('alternate_mobile')) or None
        email_val = _clean_na(rec.get('email')) or None
        circle_val = _clean_na(rec.get('circle')) or None
        addr_val = _clean_address(rec.get('address')) or None

        item = {
            'name': full_nm,
            'first_name': first_nm,
            'middle_name': mid_nm,
            'last_name': last_nm,
            'father_name': fname_val,
            'mobile': mob_val,
            'alternate_mobile': alt_val,
            'email': email_val,
            'circle': circle_val,
            'address': addr_val,
        }
        norm.append(item)

    total = len(norm)
    total_pages = max(1, (total + per_page - 1) // per_page) if total else 1
    page = max(1, min(page, total_pages))
    start = (page - 1) * per_page
    end = min(start + per_page, total)
    page_recs = norm[start:end]

    if not page_recs:
        err_json = json.dumps({
            'status': 'FAILED',
            'type': 'Number to Info',
            'total_records': 0,
            'result': [],
            'developer': f'@{bn}',
        }, indent=2, ensure_ascii=False)
        txt = f"{header}<pre><code class=\"language-json\">{_html.escape(err_json)}</code></pre>{footer}"
        return (txt, 1, False, False)

    out_payload = {
        'status': 'SUCCESS',
        'type': 'Number to Info',
        'total_records': total,
        'result': page_recs,
        'developer': f'@{bn}',
    }
    if total_pages > 1:
        out_payload['page'] = f'{page}/{total_pages}'

    json_str = json.dumps(out_payload, indent=2, ensure_ascii=False)
    txt = f"{header}<pre><code class=\"language-json\">{_html.escape(json_str)}</code></pre>{footer}"
    return (txt, total_pages, page > 1, page < total_pages)

def fmt_number(d, num, s, uid=None, elapsed=None):
    """Legacy wrapper — single page (used when no pagination needed)"""
    txt, _, _, _ = fmt_number_page(d, num, 1, per_page=2, uid=uid, elapsed=elapsed)
    return txt

def _num_page_markup(uid, page, total_pages):
    """Next/Prev inline buttons for number results (group + private)"""
    mk = InlineKeyboardMarkup(row_width=2)
    btns = []
    if page > 1:
        btns.append(_IKB('Pʀᴇᴠ', style='primary', callback_data=f'numpage_{uid}_{page - 1}'))
    if page < total_pages:
        btns.append(_IKB('Nᴇxᴛ', style='primary', callback_data=f'numpage_{uid}_{page + 1}'))
    if btns:
        mk.row(*btns)
        return mk
    return None

def _send_number_result(chat_id, msg_id, res, num, uid, elapsed, edit=True):
    """Format page 1, cache, attach Next/Prev if multi-page"""
    rtxt, total_pages, _, has_next = fmt_number_page(res, num, 1, per_page=2, uid=uid, elapsed=elapsed)
    _num_cache[uid] = {'data': res, 'num': num, 'page': 1, 'total': total_pages, 'elapsed': elapsed}
    mk = _num_page_markup(uid, 1, total_pages)
    try:
        if edit and msg_id:
            bot.edit_message_text(rtxt, chat_id, msg_id, reply_markup=mk, parse_mode='HTML')
        else:
            bot.send_message(chat_id, rtxt, reply_markup=mk, parse_mode='HTML')
    except Exception:
        try:
            bot.send_message(chat_id, rtxt, reply_markup=mk, parse_mode='HTML')
        except Exception:
            pass
    return (rtxt, total_pages)
_num_cache = {}

def fmt_aadhar(r, an, s):

    def _pe(*args, **kwargs): return ""
    _L = _pe('5465270065102334742', '') * 10
    if not r or not r.get('success'):
        return f"<blockquote>{_L}\n{_pe('5434141689558166981', '')} 𝗔𝗔𝗗𝗛𝗔𝗥 𝗜𝗡𝗙𝗢\n{_L}\n\n❌ No Data Found\n🆔 <code>{an}</code>\n\n{_L}\n{_credit()}</blockquote>"
    dl = r.get('data', []) or []
    tot = r.get('total_records', len(dl))
    txt = f"<blockquote>{_L}\n{_pe('5434141689558166981', '')} 𝗔𝗔𝗗𝗛𝗔𝗥 𝗜𝗡𝗙𝗢\n{_L}\n{_pe('5379999674193172777', '')} Qᴜᴇʀʏ : <code>{an}</code>\n{_pe('5197269100878907942', '')} Rᴇᴄᴏʀᴅꜱ : <b>{tot}</b>\n"
    for i, rec in enumerate(dl[:5], 1):
        txt += f"\n━━━━━━━━━━━━━━━━━━\n{_pe('5249231689695115145', '')} Rᴇᴄᴏʀᴅ {i}/{tot}\n━━━━━━━━━━━━━━━━━━\n{_pe('5425124408786197150', '')} Nᴀᴍᴇ : <b>{rec.get('name') or 'N/A'}</b>\n{_pe('5258513401784573443', '')} Fᴀᴛʜᴇʀ : {rec.get('father_name') or rec.get('fname') or 'N/A'}\n{_pe('6026092115631543342', '')} Mᴏʙɪʟᴇ : <code>{rec.get('mobile') or rec.get('phone') or 'N/A'}</code>\n{_pe('4958485609464202497', '')} Aᴅᴅʀᴇꜱꜱ : {rec.get('address') or 'N/A'}\n"
    txt += f'\n{_L}\n{_credit()}</blockquote>'
    return txt

def fmt_instagram(r, un, s):
    _insta_PE = ''
    if not r:
        return (f"<blockquote>📋 {_insta_PE} <b>{_s('INSTAGRAM INFO')}</b>\n\n❌ {_s('No Data')}\n{_insta_PE} @{un}\n\n{_F}\n{_credit()}</blockquote>", None)
    pic = r.get('pic')
    if pic and (not pic.startswith('http')):
        pic = None
    _insta_L = '' * 10
    txt = f"<blockquote>📋 {_insta_PE} <b>{_s('INSTAGRAM INFO')}</b>\n\n👤 <b>{_s('PROFILE DETAILS')}</b>\n├👤 {_s('USERNAME')}: @{r.get('username', 'N/A')}\n├👑 {_s('NAME')}: {r.get('name', 'N/A')}\n├🆔 {_s('ID')}: <code>{r.get('id', 'N/A')}</code>\n├✅ {_s('VERIFIED')}: {(' ' + _s('Yes') if r.get('verified') else ' ' + _s('No'))}\n├🔒 {_s('PRIVATE')}: {(' ' + _s('Yes') if r.get('private') else ' ' + _s('No'))}\n├👥 {_s('FOLLOWERS')}: {r.get('followers', 0)}\n├➡️ {_s('FOLLOWING')}: {r.get('following', 0)}\n├📸 {_s('POSTS')}: {r.get('posts', 0)}\n└📝 {_s('BIO')}: {r.get('bio', 'None')}\n\n{_insta_L}\n{_credit()}</blockquote>"
    return (txt, pic)

def fmt_ff(r, uid_ff, s):
    if not r or not r.get('success'):
        return ('<blockquote>' + _CL_TOP() + f'\n│  🎮 FREE FIRE INFO\n' + _CL_BOT() + f'\n\n❌ No Data Found\n🆔 UID: <code>{uid_ff}</code>\n\n{_F}\n{_credit()}</blockquote>', None)
    now = _now_ist()
    ban = r.get('ban_status', 'UNKNOWN')
    ban_str = ' BANNED' if 'BAN' in str(ban).upper() and 'NOT' not in str(ban).upper() else ' NOT BANNED'
    p1 = '<blockquote>' + _CL_TOP() + f'\n│  🎮 <b>FREE FIRE INFO</b> 🔥\n' + _CL_BOT() + f"\n🕐 {now}\n\n╭─── 👤 <b>PLAYER</b> ───╮\n│ 🏷️ Name    : <b>{r.get('nickname', 'N/A')}</b>\n│ 🆔 UID     : <code>{r.get('uid', uid_ff)}</code>\n│ 🌍 Region  : {r.get('region', 'N/A')}\n│ 🎖️ Level   : {r.get('level', 0)}\n│ 📈 XP      : {r.get('exp', 0):,}\n│ 👍 Likes   : {r.get('liked', 0):,}\n│ 🏆 Badges  : {r.get('badges', 0)}\n│ ⭐ Credit  : {r.get('credit_score', 0)}\n│ 📱 Version : {r.get('version', 'N/A')}\n│ 🛡️ Ban     : {ban_str}\n╰──────────────────╯\n\n╭─── 🏆 <b>RANK</b> ───╮\n│ 🎯 BR Rank : {r.get('rank_name', 'N/A')} ({r.get('rank_pts', 0)} pts)\n│ 🎯 CS Rank : {r.get('cs_rank_name', 'N/A')} ({r.get('cs_rank_pts', 0)} pts)\n│ 🥇 Max BR  : {r.get('max_br_name', 'N/A')}\n│ 🥇 Max CS  : {r.get('max_cs_name', 'N/A')}\n╰──────────────────╯\n\n╭─── 💬 <b>SOCIAL</b> ───╮\n│ ✍️ Bio     : {r.get('signature', '—') or '—'}\n│ 🌐 Lang    : {r.get('language', 'N/A')}\n│ 🎮 Mode    : {r.get('mode', 'BR')}\n╰──────────────────╯\n\n╭─── 🐾 <b>PET</b> ───╮\n│ 🆔 ID      : {r.get('pet_id', 0)}\n│ 🎖️ Level   : {r.get('pet_level', 0)}\n│ 📈 EXP     : {r.get('pet_exp', 0)}\n╰──────────────────╯\n\n╭─── ⚔️ <b>CLAN</b> ───╮\n│ 🏰 Name    : {r.get('clan_name', 'No Clan')}\n│ 🆔 ID      : <code>{r.get('clan_id', 'N/A') or 'N/A'}</code>\n│ 🏅 Level   : {r.get('clan_level', 0)}\n│ 👥 Members : {r.get('clan_members', 0)}\n│ 👑 Leader  : {r.get('clan_leader', 'N/A') or 'N/A'}\n╰──────────────────╯\n\n╭─── 📅 <b>DATES</b> ───╮\n│ 📅 Created : {r.get('create_at', 'N/A')}\n│ 🕒 Login   : {r.get('last_login', 'N/A')}\n╰──────────────────╯\n\n{_F}\n{_credit()}</blockquote>"
    p2 = None
    return (p1, p2)

def fmt_ff_like(r, uid_ff, s, likes_before=0):
    now = _now_ist()
    if not r or not r.get('success'):
        return '<blockquote>' + _CL_TOP() + f'\n│  ❤️ FF LIKE\n' + _CL_BOT() + f'\n\n❌ Like Failed!\n🆔 UID: <code>{uid_ff}</code>\n\n{_F}\n{_credit()}</blockquote>'
    cooldown = r.get('cooldown', False)
    cooldown_time = r.get('cooldown_time', '')
    try_after = r.get('try_after', 0)
    msg = r.get('message', 'Like sent!') or ''
    err = r.get('error', '') or ''
    nickname = r.get('nickname', '') or ''
    level = r.get('level', 0) or 0
    lb = int(r.get('likes_before', 0) or likes_before or 0)
    la = int(r.get('likes_after', 0) or 0)
    lg = int(r.get('likes_given', 0) or 0)
    if lb and la and (not lg):
        try:
            lg = la - lb
        except:
            pass
    if lb and lg and (not la):
        try:
            la = lb + lg
        except:
            pass
    if cooldown:
        h = 0
        m = 0
        if try_after:
            try:
                h = int(try_after) // 60
                m = int(try_after) % 60
            except:
                pass
        time_str = f'{h}h {m}m' if h else f'{m}m'
        if cooldown_time:
            time_str = cooldown_time
        return '<blockquote>' + _CL_TOP() + f'\n│  ⏰ <b>COOLDOWN ACTIVE</b>\n' + _CL_BOT() + f"\n\n❌ You cannot send likes yet!\n\n⏱️ <b>Time Remaining:</b> {time_str}\n🆔 <b>UID:</b> <code>{uid_ff}</code>\n{(' <b>Player:</b> ' + nickname + chr(10) if nickname else '')}\n📌 Next available: After 12 hours cooldown\n💡 Different UIDs also require cooldown!\n\n{_F}\n{_credit()}</blockquote>"
    status_line = ' <b>LIKE SENT!</b> ' if not err else ' <b>LIKE SENT FAILED</b> '
    total_given = lg
    likes_banner = f'\n' + _CL_TOP() + f'\n   🎉  <b>TOTAL : +{total_given} LIKES !</b> 💥\n' + _CL_BOT() + '\n' if total_given > 0 else ''
    return '<blockquote>' + _CL_TOP() + f'\n   ❤️ <b>FF LIKE</b>\n' + _CL_BOT() + f"\n\n{status_line}\n\n╭─── 👤 <b>PLAYER INFO</b> ───╮\n{('│  ɴᴀᴍᴇ  : <b>' + nickname + '</b>' + chr(10) if nickname else '')}│ 🆔 UID   : <code>{uid_ff}</code>\n{('│  ʟᴇᴠᴇʟ : <b>' + str(level) + '</b>' + chr(10) if level else '')}╰──────────────────────╯\n\n╭─── ❤️ <b>LIKE DETAILS</b> ───╮\n│ 👍 Likes Before : {lb}\n│ ❤️ Likes After  : {la}\n│ ➕ Likes Given  : {lg}\n╰──────────────────────╯{likes_banner}\n🕐 {now}\n{_F}\n{_credit()}</blockquote>"

def fmt_vehicle(r, rc, s):

    def _pe(*args, **kwargs): return ""
    _L = _pe('5465270065102334742', '') * 10
    if not r or not r.get('success'):
        return f"<blockquote>{_L}\n{_pe('5350820491017874900', '')} 𝗩𝗘𝗛𝗜𝗖𝗟𝗘 𝗜𝗡𝗙𝗢\n{_L}\n\n❌ No Data Found\n🚗 <code>{rc}</code>\n\n{_L}\n{_credit()}</blockquote>"
    return f"<blockquote>{_L}\n{_pe('5350820491017874900', '')} 𝗩𝗘𝗛𝗜𝗖𝗟𝗘 𝗜𝗡𝗙𝗢\n{_L}\n{_pe('5379999674193172777', '')} RC : <code>{rc}</code>\n{_pe('5425124408786197150', '')} Oᴡɴᴇʀ : <b>{r.get('owner_name') or 'N/A'}</b>\n{_pe('6026092115631543342', '')} Mᴏʙɪʟᴇ : <code>{r.get('mobile_number') or r.get('mobile') or 'N/A'}</code>\n{_pe('5350820491017874900', '')} Mᴏᴅᴇʟ : {r.get('vehicle_model') or r.get('model') or 'N/A'}\n{_pe('5197269100878907942', '')} Rᴇɢ Dᴀᴛᴇ : {r.get('registration_date') or r.get('reg_date') or 'N/A'}\n{_pe('5895476993314524652', '')} Fᴜᴇʟ : {r.get('fuel_type') or 'N/A'}\n{_pe('5985796637971191405', '')} Eɴɢɪɴᴇ : <code>{r.get('engine_number') or 'N/A'}</code>\n{_pe('6129812419028982717', '')} Iɴꜱᴜʀᴀɴᴄᴇ : {r.get('insurance_valid_till') or 'N/A'}\n\n{_L}\n{_credit()}</blockquote>"
_PE_IDS = ['5888620056551625531', '5884366771913233289', '5406926593698312391', '6325767939676964769', '5253997076169115797', '5301176488756788169', '6312140764361006715', '6314298001879735512', '6314162714704878982', '6314344267267450186', '6314500762990811983', '6311939527963319025', '6314409378971657327', '5310162878894999252', '5395779525772599106', '5350820491017874900', '6120410409200521433', '6238011071941057341', '5267193101193083992', '5224450179368767019', '5197269100878907942', '5332455502917949981', '5195033767969839232', '5197288647275071607']

def _rpe():
    """Random premium emoji id from list"""
    return random.choice(_PE_IDS)

def kb_p1(uid):
    mk=ReplyKeyboardMarkup(resize_keyboard=True,row_width=1)
    mk.row(_KB("ɴᴜᴍʙᴇʀ ɪɴꜰᴏ", style="primary"))
    mk.row(_KB("ᴅᴀɪʟʏ ꜱᴘɪɴ", style="primary"))
    mk.row(_KB("ʀᴇᴅᴇᴇᴍ ᴄᴏᴅᴇ", style="primary"))
    mk.row(_KB("ʀᴇꜰᴇʀ & ᴇᴀʀɴ", style="primary"))
    mk.row(_KB("ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ", style="primary"))
    mk.row(_KB("ꜱᴜᴩᴩᴏʀᴛ", style="success"))
    if is_admin(uid):
        mk.row(_KB("ᴀᴅᴍɪɴ ᴩᴀɴᴇʟ", style="success"))
    return mk
def kb_admin_p1():
    mk = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    mk.row(_KB('ᴅᴀꜱʜʙᴏᴀʀᴅ', style='primary'), _KB('ʟɪᴠᴇ ꜱᴛᴀᴛꜱ', style='primary'))
    mk.row(_KB('ᴜꜱᴇʀ ʟɪꜱᴛ', style='primary'), _KB('ʜɪꜱᴛᴏʀʏ', style='primary'))
    mk.row(_KB('ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴍᴇɴᴜ', style='primary'), _KB('ʀᴇᴅᴇᴇᴍ ᴍᴇɴᴜ', style='success'))
    mk.row(_KB('ᴄʀᴇᴅɪᴛꜱ ᴍᴇɴᴜ', style='primary'), _KB('ᴩʀᴇᴍɪᴜᴍ ᴍᴇɴᴜ', style='primary'))
    mk.row(_KB('ǫᴜɪᴄᴋ ʙᴀɴ', style='danger'), _KB('ᴜɴʙʟᴏᴄᴋ ᴜꜱᴇʀ', style='success'))
    mk.row(_KB('ᴀᴅᴍɪɴ ᴩᴀɢᴇ 2', style='danger'), _KB('ᴍᴀɪɴ ᴍᴇɴᴜ', style='danger'))
    return mk

def kb_admin_p2():
    mk = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    mk.row(_KB('ᴄʜᴀɴɴᴇʟ ᴍᴇɴᴜ', style='primary'), _KB('ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ ᴍᴏᴅᴇ', style='danger'))
    mk.row(_KB('ʀᴇꜰᴇʀʀᴀʟ ꜱᴇᴛᴛɪɴɢ', style='success'), _KB('ᴀᴅᴍɪɴ', style='primary'))
    mk.row(_KB('ᴀᴅᴍɪɴ ᴩᴀɢᴇ 1', style='danger'), _KB('ᴍᴀɪɴ ᴍᴇɴᴜ', style='danger'))
    return mk


def kb_group_mgmt():
    mk=ReplyKeyboardMarkup(resize_keyboard=True,row_width=2)
    mk.row(_KB(' VIEW GROUPS',style='success'),_KB(' ADD GROUP',style='success'))
    mk.row(_KB(' GROUP CONTROL',style='primary'))
    mk.row(_KB(' BACK TO ADMIN P2',style='danger'))
    return mk

def kb_welcome():
    mk=ReplyKeyboardMarkup(resize_keyboard=True,row_width=2)
    mk.row(_KB(' SET WELCOME IMAGE',style='success'),_KB(' SET WELCOME VIDEO',style='success'))
    mk.row(_KB(' SET WELCOME CAPTION',style='success'),_KB(' SET FIRST TIME STICKER',style='success'))
    mk.row(_KB(' RESET TO DEFAULT',style='danger'))
    mk.row(_KB(' BACK TO ADMIN P2',style='danger'))
    return mk

def kb_group_welcome():
    mk=ReplyKeyboardMarkup(resize_keyboard=True,row_width=2)
    mk.row(_KB(' GROUP IMAGE SET',style='success'),_KB(' GROUP VIDEO SET',style='success'))
    mk.row(_KB(' GROUP VIDEO LIST',style='success'),_KB(' GROUP STICKER SET',style='success'))
    mk.row(_KB(' GROUP WELCOME TEXT',style='success'),_KB(' GROUP WELCOME RESET',style='danger'))
    mk.row(_KB(' BACK TO ADMIN P2',style='danger'))
    return mk

def kb_admin_mgmt():
    mk=ReplyKeyboardMarkup(resize_keyboard=True,row_width=2)
    mk.row(_KB(' ADD ADMIN',style='success'),_KB(' REMOVE ADMIN',style='danger'))
    mk.row(_KB(' ADMIN LIST',style='primary'))
    mk.row(_KB(' BACK TO ADMIN P2',style='danger'))
    return mk

def kb_channel_mgmt():
    mk=ReplyKeyboardMarkup(resize_keyboard=True,row_width=2)
    mk.row(_KB('📢 CHANNEL ADMIN',style='primary'),_KB('👥 GROUP ADMIN',style='primary'))
    mk.row(_KB(' BACK TO ADMIN P2',style='danger'))
    return mk

def kb_features():
    enabled=dict(get_all_feature_states()).get('number',True)
    mk=InlineKeyboardMarkup(row_width=1)
    mk.add(_IKB(' Number Info ' + (' ON' if enabled else ' OFF'),style='success' if enabled else 'danger',callback_data='ftog_number'))
    mk.add(_IKB(' BACK TO ADMIN P2',style='danger',callback_data='ftog_back'))
    return mk

def kb_groups_inline(page=1):
    groups = get_all_groups()
    if not groups:
        return None
    pp = 5
    st = (page - 1) * pp
    en = st + pp
    tp = (len(groups) + pp - 1) // pp
    mk = InlineKeyboardMarkup(row_width=1)
    for gid, title in groups[st:en]:
        g = get_group(gid)
        s = safe_g(g, 7)
        bl = safe_g(g, 6)
        mu = safe_g(g, 8)
        mi = '' if mu == 1 else ''
        _blk = '' if bl == 1 else ''
        dn = title[:20] + '...' if len(title) > 20 else title
        mk.add(_IKB(f'📌 {dn} | S:{s} {_blk}{mi}', style='primary', callback_data=f'grp_sel_{gid}'))
    nav = []
    if page > 1:
        nav.append(_IKB('Pʀᴇᴠ', callback_data=f'grp_pg_{page - 1}'))
    nav.append(_IKB(f'{page}/{tp}', callback_data='noop'))
    if en < len(groups):
        nav.append(_IKB('Nᴇxᴛ', callback_data=f'grp_pg_{page + 1}'))
    if len(nav) > 1:
        mk.row(*nav)
    mk.add(_IKB(' BACK TO ADMIN P2', style='danger', callback_data='grp_back_menu'))
    return mk

def kb_group_ctrl(gid):
    g = get_group(gid)
    if not g:
        return None
    bl = safe_g(g, 6)
    mu = safe_g(g, 8)
    mk = InlineKeyboardMarkup(row_width=2)
    mk.add(_IKB(' UNBLOCK' if bl else ' BLOCK', style='danger', callback_data=f'grp_blk_{gid}'), _IKB(' UNMUTE' if mu else ' MUTE', style='primary', callback_data=f'grp_mute_{gid}'))
    mk.add(_IKB(' INFO', style='primary', callback_data=f'grp_info_{gid}'))
    mk.add(_IKB(' BACK TO LIST', style='danger', callback_data='grp_back_list'))
    return mk

def refresh_group_msg(chat_id, msg_id, gid):
    g = get_group(gid)
    title = next((t for gi, t in get_all_groups() if gi == gid), 'Unknown')
    if not g:
        return
    bl = safe_g(g, 6)
    s = safe_g(g, 7)
    mu = safe_g(g, 8)
    txt = f"<blockquote>👥 <b>ɢʀᴏᴜᴩ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>\n\n📌 <b>{title}</b>\n🆔 <code>{gid}</code>\n{_F}\n🚫 Block: {(' YES' if bl else ' NO')} | 🔇 Mute: {(' YES' if mu else ' NO')}\n🔍 Total Searches: <code>{s}</code>\n{_F}\n⚡ @notCoder2006</blockquote>"
    try:
        bot.edit_message_text(txt, chat_id, msg_id, reply_markup=kb_group_ctrl(gid), parse_mode='HTML')
    except:
        pass

def kb_menu_p1(uid=None):
    mk=InlineKeyboardMarkup(row_width=1)
    mk.add(_IKB("ɴᴜᴍʙᴇʀ ɪɴꜰᴏ", style="primary", callback_data="menu_number"))
    mk.add(_IKB("ᴅᴀɪʟʏ ꜱᴘɪɴ", style="primary", callback_data="menu_spin"))
    mk.add(_IKB("ʀᴇᴅᴇᴇᴍ ᴄᴏᴅᴇ", style="primary", callback_data="menu_redeem"))
    mk.add(_IKB("ʀᴇꜰᴇʀ & ᴇᴀʀɴ", style="primary", callback_data="menu_refer"))
    mk.add(_IKB("ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ", style="primary", callback_data="menu_leaderboard"))
    mk.add(_IKB("ꜱᴜᴩᴩᴏʀᴛ", style="success", callback_data="menu_support"))
    mk.add(_IKB("ᴄʟᴏꜱᴇ", style="danger", callback_data="menu_close"))
    return mk



def _clear_telegram_command_menu():
    """Clear Telegram command lists from all relevant scopes. Telegram may still show the client Menu affordance itself."""
    base = f'https://api.telegram.org/bot{BOT_TOKEN}'
    scopes = [
        {'type': 'default'},
        {'type': 'all_private_chats'},
        {'type': 'all_group_chats'},
    ]
    for scope in scopes:
        try:
            r = requests.post(base + '/deleteMyCommands', json={'scope': scope}, timeout=10)
            if r.status_code != 200:
                print(f'[TG_MENU] deleteMyCommands {scope}: {r.text[:200]}')
        except Exception as e:
            print(f'[TG_MENU] deleteMyCommands {scope}: {e}')
    # Reset to Telegram's default menu behavior after command lists are cleared.
    try:
        requests.post(base + '/setChatMenuButton', json={'menu_button': {'type': 'default'}}, timeout=10)
    except Exception as e:
        print(f'[TG_MENU] reset menu button: {e}')

def _send_saved_group_media(chat_id, media_ref, media_type, caption=None, reply_markup=None):
    """Send a stored group welcome media reference. Supports Telegram file IDs and legacy local files."""
    if not media_ref:
        return False
    try:
        ref=str(media_ref)
        kwargs={}
        if caption is not None:
            kwargs['caption']=caption; kwargs['parse_mode']='HTML'
        if reply_markup is not None:
            kwargs['reply_markup']=reply_markup
        if ref.startswith('fileid:'):
            fid=ref[7:]
            if media_type=='video': bot.send_video(chat_id,fid,**kwargs)
            elif media_type=='photo': bot.send_photo(chat_id,fid,**kwargs)
            else: return False
            return True
        if os.path.exists(ref):
            with open(ref,'rb') as fh:
                if media_type=='video': bot.send_video(chat_id,fh,**kwargs)
                elif media_type=='photo': bot.send_photo(chat_id,fh,**kwargs)
                else: return False
            return True
    except Exception:
        return False
    return False

@bot.message_handler(commands=['start'])
def cmd_start(msg):
    try:
        if msg.chat.type == 'channel':
            return
        uid = msg.from_user.id
        uname = msg.from_user.username or ''
        fname = _html.escape(msg.from_user.first_name or 'User')
        parts = msg.text.split()
        start_param = parts[1] if len(parts) > 1 else None
        if start_param and start_param.startswith('verify_'):
            token = start_param[7:]
            today = datetime.now().strftime('%Y-%m-%d')
            if not get_user(uid):
                add_user(uid, uname, fname, None)
            row = c.execute('SELECT user_id FROM verify_tokens WHERE token=?', (token,)).fetchone()
            if not row:
                bot.reply_to(msg, '<blockquote> Invalid verify link!</blockquote>', parse_mode='HTML')
                return
            if row[0] != uid:
                bot.reply_to(msg, '<blockquote> Ye link tumhara nahi hai!</blockquote>', parse_mode='HTML')
                return
            if c.execute('SELECT id FROM verify_claims WHERE user_id=? AND claim_date=?', (uid, today)).fetchone():
                bot.reply_to(msg, '<blockquote> Aaj already verify kar chuke ho!</blockquote>', parse_mode='HTML')
                return
            c.execute('INSERT INTO verify_claims(user_id, claim_date) VALUES (?,?)', (uid, today))
            c.execute('UPDATE users SET credits = credits + 5 WHERE user_id=?', (uid,))
            c.execute('DELETE FROM verify_tokens WHERE token=?', (token,))
            conn.commit()
            bot.reply_to(msg, f'<blockquote>{_F}\n✅ 𝐕𝐞𝐫𝐢𝐟𝐢𝐜𝐚𝐭𝐢𝐨𝐧 𝐒𝐮𝐜𝐜𝐞𝐬𝐬𝐟𝐮𝐥!\n{_F}\n\n🎉 <b>+5 Credits</b> mil gaye!\n📅 Kal dobara verify kar sakte ho.\n{_F}\n👨\u200d💻 𝐃𝐄𝐕 : @notCoder2006</blockquote>', parse_mode='HTML')
            return
        try:
            if True:
                bot.set_message_reaction(msg.chat.id, msg.message_id, [telebot.types.ReactionTypeEmoji('😍')], is_big=True)
        except:
            pass
        if msg.chat.type in ['group', 'supergroup']:
            add_group_to_db(msg.chat.id, msg.chat.title or 'Unknown', uid)
            user = get_user(uid)
            if not user:
                add_user(uid, uname, fname)
            credits = get_credits(uid)
            try:
                bn = _get_bot_username()
            except:
                bn = '𝙽𝚘𝚝 𝙲𝚘𝚍𝚎𝚛'
            st = get_welcome_settings()
            wvid = st[4] if st else None
            wimg = st[3] if st else None
            cr_disp = '∞' if is_admin(uid) else str(credits)

            def _te(*args, **kwargs): return ""
            E11 = '5041866884778034602'
            E13 = '6145434301711259786'
            txt = f"""<blockquote>╭━━━━━━━━━━━━━✦\n│ {_te(E11)} ᴍᴇɴᴜ ᴏᴩᴇɴᴇᴅ!\n╰━━━━━━━━━━━━━✦\n\n👤 ɴᴀᴍᴇ : <a href='tg://user?id={uid}'><b>{fname}</b></a>\n✏ ɪᴅ   : <code>{uid}</code>\n\n🪙 ᴄʀᴇᴅɪᴛꜱ : {cr_disp}\n━━━━━━━━━━━━━━━━━━\n{_te(E13)} ᴄʟɪᴄᴋ ʙᴜᴛᴛᴏɴ ᴛᴏ ᴜꜱᴇ ꜰᴇᴀᴛᴜʀᴇ:\n</blockquote>"""
            grp_mk = InlineKeyboardMarkup(row_width=2)
            grp_mk.add(_IKB('ɴᴜᴍʙᴇʀ ɪɴꜰᴏ', style='primary', callback_data=f'grp_num_{uid}_{msg.chat.id}'))
            grp_mk.row(_IKB('ᴛɢ ɪᴅ ɪɴꜰᴏ', style='primary', callback_data=f'grp_usr_{uid}_{msg.chat.id}'), _IKB('ꜱᴇʟᴇᴄᴛ ᴜꜱᴇʀ', style='primary', url=f'https://t.me/{bn}?start=dm_selectuser'))
            grp_mk.row(_IKB('ɪɴꜱᴛᴀ ɪɴꜰᴏ', style='primary', callback_data=f'grp_insta_{uid}_{msg.chat.id}'), _IKB('ᴅᴀɪʟʏ ꜱᴘɪɴ', style='primary', callback_data=f'grp_spn_{uid}_{msg.chat.id}'))
            grp_mk.row(_IKB('ʙᴏᴍʙᴇʀ', style='primary', callback_data=f'grp_bomb_{uid}_{msg.chat.id}'))
            grp_mk.add(_IKB('ᴄʟᴏꜱᴇ', style='danger', callback_data=f'grp_cls_{uid}'))
            gwimg2, gwvid2, gwvlist2, gwstk2 = get_group_welcome_media(msg.chat.id)
            _grp_sent = False
            if gwvlist2:
                _fid2 = get_next_group_video(msg.chat.id)
                if _fid2:
                    try:
                        bot.send_video(msg.chat.id, _fid2, caption=txt, reply_markup=grp_mk, parse_mode='HTML')
                        _grp_sent = True
                    except:
                        pass
            if not _grp_sent and gwvid2:
                _grp_sent = _send_saved_group_media(msg.chat.id, gwvid2, 'video', txt, grp_mk)
            if not _grp_sent and gwimg2:
                _grp_sent = _send_saved_group_media(msg.chat.id, gwimg2, 'photo', txt, grp_mk)
            if not _grp_sent and wvid:
                _grp_sent = _send_saved_group_media(msg.chat.id, wvid, 'video', txt, grp_mk)
            if not _grp_sent and wimg:
                _grp_sent = _send_saved_group_media(msg.chat.id, wimg, 'photo', txt, grp_mk)
            if not _grp_sent:
                _send_react(msg.chat.id, txt, reply_markup=grp_mk, parse_mode='HTML')
            return
        ref = None
        if len(msg.text.split()) > 1:
            param = msg.text.split()[1]
            if param == 'dm_selectuser':
                bot.send_message(uid, '<blockquote> <b>ꜱᴇʟᴇᴄᴛ ᴜꜱᴇʀ</b>\nNeeche button dabao:</blockquote>', reply_markup=kb_select_user(), parse_mode='HTML')
                return
            try:
                ref = int(param)
                if ref == uid:
                    ref = None
            except:
                pass
        try:
            _fj_chs = get_force_join_channels()
            _fj_channels_exist = bool(_fj_chs)
        except Exception as _fje:
            print(f'[FJ_CHECK] {_fje}')
            _fj_channels_exist = False
        if _fj_channels_exist:
            try:
                _not_joined = not check_channel(uid)
            except Exception as _cce:
                print(f'[CHECK_CH] {_cce}')
                _not_joined = False
            if _not_joined:
                try:
                    mk = get_channels_keyboard(uid)
                except Exception as _mke:
                    print(f'[CH_KB] {_mke}')
                    mk = None
                if mk:
                    if ref:
                        user_state[uid] = {'pending_ref': ref}
                    _safe_send(uid, format_force_join_msg(), reply_markup=mk, parse_mode='HTML')
                    return
        user = get_user(uid)
        is_first = not user
        if not user:
            add_user(uid, uname, fname, ref)
        else:
            is_first = user[10] == 1 if user and len(user) > 10 else True
        credits = get_credits(uid)
        st = get_welcome_settings()
        wvid = st[4] if st else None
        wimg = st[3] if st else None
        try:
            wtxt = format_welcome(uid, fname, credits, uname)
        except Exception as _fwe:
            print(f'[FORMAT_WELCOME] {_fwe}')
            wtxt = f"<blockquote>👋 ʜᴇʟʟᴏ <a href='tg://user?id={uid}'><b>{fname}</b></a>!\n\n💰 Credits: {credits}\n\n⚡ @notCoder2006</blockquote>"
        wtxt_plain_cap = f"👋 ʜᴇʟʟᴏ <a href='tg://user?id={uid}'><b>{fname}</b></a>!\n\n💰 ᴄʀᴇᴅɪᴛꜱ: {credits}\n⚡ @notCoder2006"
        try:
            rl = f'https://t.me/{_get_bot_username()}?start={uid}'
        except:
            rl = f'https://t.me/bot?start={uid}'
        rmk = kb_p1(uid)
        stk = get_first_time_sticker()
        if stk:
            try:
                bot.send_sticker(uid, stk)
            except:
                pass
        sent = False
        _wv_fid = _welcome_fileid_cache.get('video')
        _wi_fid = _welcome_fileid_cache.get('image')
        if _wv_fid:
            try:
                bot.send_video(uid, _wv_fid, caption=wtxt, parse_mode='HTML', reply_markup=rmk, has_spoiler=True, message_effect_id='5046509860389126442')
                sent = True
            except Exception as _e1:
                _welcome_fileid_cache.pop('video', None)
                print(f'[START_VID_FID] {_e1}')
        if not sent and _wi_fid:
            try:
                bot.send_photo(uid, _wi_fid, caption=wtxt, parse_mode='HTML', reply_markup=rmk, has_spoiler=True, message_effect_id='5046509860389126442')
                sent = True
            except Exception as _e2:
                _welcome_fileid_cache.pop('image', None)
                print(f'[START_IMG_FID] {_e2}')
        if not sent and wvid:
            try:
                cap=_welcome_media_caption(uid, fname, uname, credits, wtxt)
                if str(wvid).startswith('fileid:'):
                    sm=bot.send_video(uid,str(wvid)[7:],caption=cap,parse_mode='HTML',reply_markup=rmk,has_spoiler=True,message_effect_id='5046509860389126442')
                elif os.path.exists(wvid):
                    with open(wvid,'rb') as f: sm=bot.send_video(uid,f,caption=cap,parse_mode='HTML',reply_markup=rmk,has_spoiler=True,message_effect_id='5046509860389126442')
                    if sm and sm.video:
                        _welcome_fileid_cache['video'] = sm.video.file_id
                    sent = True
            except Exception as _e3:
                print(f'[START_VID] {_e3}')
        if not sent and wimg:
            try:
                cap=_welcome_media_caption(uid, fname, uname, credits, wtxt)
                if str(wimg).startswith('fileid:'):
                    sm=bot.send_photo(uid,str(wimg)[7:],caption=cap,parse_mode='HTML',reply_markup=rmk,has_spoiler=True,message_effect_id='5046509860389126442')
                elif os.path.exists(wimg):
                    with open(wimg,'rb') as f: sm=bot.send_photo(uid,f,caption=cap,parse_mode='HTML',reply_markup=rmk,has_spoiler=True,message_effect_id='5046509860389126442')
                    if sm and sm.photo:
                        _welcome_fileid_cache['image'] = sm.photo[-1].file_id
                    sent = True
            except Exception as _e4:
                print(f'[START_IMG] {_e4}')
        if sent:
            pass
        if not sent:
            try:
                _wm2 = _send_react(uid, wtxt, reply_markup=rmk, parse_mode='HTML', message_effect_id='5046509860389126442')
                sent = True
                if _wm2:
                    try:
                        bot.set_message_reaction(uid, _wm2.message_id, [telebot.types.ReactionTypeEmoji('😍')], is_big=True)
                    except:
                        pass
            except Exception as _e6:
                print(f'[START_TXT] {_e6}')
                try:
                    import re as _re5
                    _plain = _re5.sub('<[^>]+>', '', wtxt)
                    bot.send_message(uid, _plain, reply_markup=rmk)
                except:
                    pass
        if is_first:
            update_user(uid, first_time=0)
    except Exception as _start_e:
        import traceback
        traceback.print_exc()
        print(f'[CMD_START] {_start_e}')
        try:
            bot.send_message(msg.chat.id, '<blockquote> Kuch error hua, dobara /start karo!\n @notCoder2006</blockquote>', parse_mode='HTML')
        except:
            pass

@bot.message_handler(commands=['menu'])
def cmd_menu(msg):
    uid = msg.from_user.id
    fname = _html.escape(msg.from_user.first_name or 'User')
    if msg.chat.type in ['group', 'supergroup']:
        return
    user = get_user(uid)
    if not user:
        try:
            bot.reply_to(msg, '<blockquote> Pehle bot DM mein /start karo!\n @notCoder2006</blockquote>', parse_mode='HTML')
        except:
            pass
        return
    cr = get_credits(uid)
    cr_disp = '∞' if is_admin(uid) else str(cr)
    txt = f"<blockquote>🤖 ᴍᴀɪɴ ᴍᴇɴᴜ\n👇 Feature select karo:\n\n👋 ʜᴇʟʟᴏ <a href='tg://user?id={uid}'><b>{fname}</b></a>\n💰 ᴄʀᴇᴅɪᴛꜱ: <b>{cr_disp}</b>\n⚡ @notCoder2006</blockquote>"
    bot.reply_to(msg, txt, reply_markup=kb_p1(uid), parse_mode='HTML')
VIPLIKE_API_1 = 'https://like62y3.onrender.com/like'
VIPLIKE_API_2 = 'https://druu-likes-15-day.vercel.app/like'

@bot.message_handler(commands=['numinfo', 'num', 'number'])
def cmd_numinfo(msg):
    """/num 9876543210 — works private + group"""
    uid = msg.from_user.id
    if not is_feature_enabled('number'):
        bot.reply_to(msg, '<blockquote> Number feature is OFF\n @notCoder2006</blockquote>', parse_mode='HTML')
        return
    if check_blocked_and_reply(uid):
        return
    raw = (msg.text or '').strip()
    parts = raw.split()
    if len(parts) < 2:
        bot.reply_to(msg, f'<blockquote>📞 <b>NUMBER INFO</b>\n\nUsage: <code>/num 9876543210</code>\nExample: <code>/num 9876543210</code>\n\n⚡ @notCoder2006</blockquote>', parse_mode='HTML')
        return
    num = re.sub('\\D', '', parts[1])
    if len(num) == 12 and num.startswith('91'):
        num = num[2:]
    if not re.match('^[6-9]\\d{9}$', num):
        bot.reply_to(msg, '<blockquote> Invalid! 10-digit Indian number\n\u200d 𝐃𝐄𝐕 : @notCoder2006</blockquote>', parse_mode='HTML')
        return
    user = get_user(uid)
    if not user:
        add_user(uid, msg.from_user.username or '', msg.from_user.first_name or 'User')
        user = get_user(uid)
    if not deduct_credit(uid):
        txt, mk = no_credits_msg(uid)
        bot.reply_to(msg, txt, reply_markup=mk, parse_mode='HTML')
        return
    sm = bot.reply_to(msg, '<blockquote>' + pbar(0) + '\nꜱᴛᴀʀᴛɪɴɢ...</blockquote>', parse_mode='HTML')
    try:
        bot.send_chat_action(msg.chat.id, 'typing')
    except:
        pass
    _sf_ni = _start_anim(msg.chat.id, sm.message_id, 'number')
    _t0 = time.time()
    res = api_number(num)
    _elapsed = time.time() - _t0
    _sf_ni[0] = True
    if not (res and res.get('success')) and (not is_admin(uid)):
        refund_credit(uid)
    _send_number_result(msg.chat.id, sm.message_id, res, num, uid, _elapsed, edit=True)
    if res and res.get('success'):
        c.execute('INSERT INTO search_history(user_id,search_type,query,search_date,result) VALUES(?,?,?,?,?)', (uid, S_NUM, num, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), json.dumps(res)))
        conn.commit()
        log_search(uid, msg.from_user.first_name or 'User', msg.from_user.username or '', 'NUMBER', num)

@bot.message_handler(commands=['usernum', 'tg', 'tgnum', 'user'])
def cmd_usernum(msg):
    """/usernum <@username or user_id> - user number + pfp"""
    uid = msg.from_user.id
    if not is_feature_enabled('username'):
        return
    if check_blocked_and_reply(uid):
        return
    parts = msg.text.split()
    if len(parts) < 2:
        bot.reply_to(msg, f'<blockquote>{_F}\n✭ 𝗨𝗦𝗘𝗥 𝗡𝗨𝗠 𝗖𝗢𝗠𝗠𝗔𝗡𝗗\n{_F}\n\n★ 𝐔𝐬𝐚𝐠𝐞   : <code>/usernum @username</code>\n          : <code>/usernum 123456789</code>\n★ 𝐄𝐱𝐚𝐦𝐩𝐥𝐞 : <code>/usernum @durov</code>\n\n{_F}\n👨\u200d💻 𝐃𝐄𝐕 : @notCoder2006\n{_F}</blockquote>', parse_mode='HTML')
        return
    query = parts[1].strip()
    user = get_user(uid)
    if not user:
        add_user(uid, msg.from_user.username or '', msg.from_user.first_name or 'User')
        user = get_user(uid)
    if not deduct_credit(uid):
        txt, mk = no_credits_msg(uid)
        bot.reply_to(msg, txt, reply_markup=mk, parse_mode='HTML')
        return
    sm = bot.reply_to(msg, '<blockquote>' + pbar(0) + '\nꜱᴛᴀʀᴛɪɴɢ...</blockquote>', parse_mode='HTML')
    try:
        bot.send_chat_action(msg.chat.id, 'typing')
    except:
        pass
    _sf_un = _start_anim(msg.chat.id, sm.message_id, 'usernum')
    fname = _html.escape(msg.from_user.first_name or 'User')
    res = api_full_user(query)
    _sf_un[0] = True
    now = _now_ist()
    stype = S_USER if query.startswith('@') or not query.lstrip('-').isdigit() else S_TID
    _cr_left_un = get_credits(uid) if not is_admin(uid) else '∞'
    if stype == S_USER:
        rtxt, _ = _fmt_tg_user_short(res, query, now, _cr_left_un)
    else:
        rtxt, _ = _fmt_tg_user(res, '', 'USER INFO', query, now, _cr_left_un)
    if not (res and res.get('success')) and (not is_admin(uid)):
        refund_credit(uid)
    try:
        bot.edit_message_text(rtxt, msg.chat.id, sm.message_id, parse_mode='HTML')
    except:
        bot.send_message(msg.chat.id, rtxt, parse_mode='HTML')
    if res and res.get('success'):
        c.execute('INSERT INTO search_history(user_id,search_type,query,search_date,result) VALUES(?,?,?,?,?)', (uid, stype, query, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), json.dumps(res)))
        conn.commit()
        log_search(uid, fname, msg.from_user.username or '', 'USERNUM', query, None)

@bot.message_handler(commands=['unlimited'])
def cmd_unlimited(msg):
    """/unlimited on|off|list — Group unlimited toggle (admin only)"""
    uid = msg.from_user.id
    if not is_admin(uid):
        bot.reply_to(msg, '<blockquote> Sirf admin use kar sakta hai!</blockquote>', parse_mode='HTML')
        return
    parts = msg.text.split()
    usage = '<blockquote>' + _F + '\n <b>/unlimited COMMAND</b>\n' + _F + '\n\n <b>Usage:</b>\n  <code>/unlimited on &lt;group_id&gt;</code>\n  <code>/unlimited off &lt;group_id&gt;</code>\n  <code>/unlimited list</code> — sabhi groups ka status\n\n <b>Example:</b>\n  <code>/unlimited on -1001234567890</code>\n' + _F + '\n @notCoder2006</blockquote>'
    if len(parts) < 2:
        bot.reply_to(msg, usage, parse_mode='HTML')
        return
    sub = parts[1].lower()
    if sub == 'list':
        groups = get_all_groups()
        if not groups:
            bot.reply_to(msg, '<blockquote> Koi group nahi mila!</blockquote>', parse_mode='HTML')
            return
        lines = []
        for gid, title in groups:
            g = get_group(gid)
            unl = safe_g(g, 5) == 1
            icon = '' if unl else ''
            lines.append(icon + ' <code>' + str(gid) + '</code> — ' + title[:25])
        txt = '<blockquote>' + _F + '\n <b>GROUP UNLIMITED STATUS</b>\n' + _F + '\n\n' + '\n'.join(lines) + '\n' + _F + '\n @notCoder2006</blockquote>'
        bot.reply_to(msg, txt, parse_mode='HTML')
        return
    if sub not in ('on', 'off') or len(parts) < 3:
        bot.reply_to(msg, usage, parse_mode='HTML')
        return
    try:
        gid = int(parts[2])
    except:
        bot.reply_to(msg, '<blockquote> Invalid group ID! Negative integer chahiye.\nExample: <code>-1001234567890</code></blockquote>', parse_mode='HTML')
        return
    g = get_group(gid)
    if not g:
        add_group(gid, 'Group ' + str(gid), uid)
        g = get_group(gid)
    curr_unl = safe_g(g, 5) == 1
    want_on = sub == 'on'
    if curr_unl == want_on:
        state = 'ON' if want_on else 'OFF'
        bot.reply_to(msg, '<blockquote>ℹ Group <code>' + str(gid) + '</code> pehle se <b>unlimited ' + state + '</b> hai!</blockquote>', parse_mode='HTML')
        return
    toggle_group_unlimited(gid)
    new_state = ' ON' if want_on else ' OFF'
    bot.reply_to(msg, '<blockquote>' + _F + '\n <b>UNLIMITED UPDATED</b>\n' + _F + '\n\n Group ID : <code>' + str(gid) + '</code>\n Status   : <b>Unlimited ' + new_state + '</b>\n\n' + _F + '\n @notCoder2006</blockquote>', parse_mode='HTML')

@bot.message_handler(commands=['redeem'])
def cmd_redeem(msg):
    uid = msg.from_user.id
    if check_blocked_and_reply(uid):
        return
    parts = msg.text.split()
    if len(parts) < 2:
        user_state[uid] = S_REDEEM
        bot.reply_to(msg, '<blockquote> Send redeem code:\nExample: <code>NOT_CODER-XXXXXX</code>\n\u200d 𝐃𝐄𝐕 : @notCoder2006</blockquote>', parse_mode='HTML')
        return
    ok, rmsg = redeem_code_fn(uid, parts[1])
    bot.reply_to(msg, f'<blockquote>{rmsg}\n👨\u200d💻 𝐃𝐄𝐕 : @notCoder2006</blockquote>', parse_mode='HTML')

@bot.message_handler(commands=['premium'])
def cmd_premium(msg):
    uid = msg.from_user.id
    if check_blocked_and_reply(uid):
        return
    parts = msg.text.split()
    if len(parts) < 2:
        user_state[uid] = S_PREM_REDEEM
        bot.reply_to(msg, f'<blockquote>💎 <b>ᴩʀᴇᴍɪᴜᴍ ᴄᴏᴅᴇ ʀᴇᴅᴇᴇᴍ</b>\n{_F}\n📤 Send premium code:\nExample: <code>LPREM-XXXXXX</code>\n{_F}\n👨\u200d💻 𝐃𝐄𝐕 : @notCoder2006</blockquote>', parse_mode='HTML')
        return
    ok, rmsg = redeem_premium_code_fn(uid, parts[1])
    bot.reply_to(msg, f'<blockquote>{rmsg}\n👨\u200d💻 𝐃𝐄𝐕 : @notCoder2006</blockquote>', parse_mode='HTML')

@bot.message_handler(commands=['hello', 'help', 'h', 'cmd'])
def cmd_hello(msg):
    uid = msg.from_user.id
    try:
        bn = _get_bot_username()
    except:
        bn = 'bot'
    if msg.chat.type in ['group', 'supergroup']:
        gtxt = f'<blockquote>╭━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✦\n│  📋 <b>ɢʀᴏᴜᴩ ᴄᴏᴍᴍᴀɴᴅꜱ</b> ⚡\n╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✦\n\n╭─── 📱 <b>ɴᴜᴍʙᴇʀ ɪɴꜰᴏ</b> ───╮\n│ Bas number type karo:\n│ <code>9876543210</code> → Name, Operator, SIM\n╰──────────────────────────╯\n\n╭─── 👤 <b>ᴜꜱᴇʀɴᴀᴍᴇ ɪɴꜰᴏ</b> ───╮\n│ Bas @username type karo:\n│ <code>@username</code> → TG Number + Info\n╰──────────────────────────╯\n\n╭─── 🚀 <b>ᴄᴏᴍᴍᴀɴᴅꜱ</b> ───╮\n│ /start    → ᴍᴇɴᴜ\n│ /spin     → ᴅᴀɪʟʏ ꜱᴘɪɴ\n│ /freespin → ɢʀᴏᴜᴩ ꜱᴘɪɴ\n╰─────────────────╯\n\n╭─── 🎮 <b>ꜰʀᴇᴇ ꜰɪʀᴇ</b> ───╮\n│ /like <code>uid</code>     → ❤️ ʟɪᴋᴇꜱ\n│ /like <code>ind uid</code>  → ʀᴇɢɪᴏɴ\n│ /info <code>uid</code>     → 🎮 ɪɴꜰᴏ\n╰───────────────────╯\n\n╭─── 👤 <b>TG ᴜꜱᴇʀ</b> ───╮\n│ /user <code>123456789</code>\n╰────────────────────╯\n\n╭─── 💣 <b>ʙᴏᴍʙᴇʀ</b> ───╮\n│ /bomb <code>9876543210</code>\n│ /stopbomb → ʙᴀɴᴅ ᴋᴀʀᴏ\n╰──────────────────╯\n\n╭─── 📸 <b>ɪɴꜱᴛᴀɢʀᴀᴍ</b> ───╮\n│ /insta <code>username</code>\n╰────────────────────╯\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n💀 ᴅᴇᴠᴇʟᴏᴩᴇʀ : @notCoder2006</blockquote>'
        bot.reply_to(msg, gtxt, parse_mode='HTML')
        return
    txt = f'<blockquote>╭━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✦\n│  📋 <b>ꜱᴀʀᴇ ᴄᴏᴍᴍᴀɴᴅ ʟɪꜱᴛ</b> ⚡\n╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✦\n\n╭─── 🚀 <b>MAIN</b> ───╮\n│ /start   → ʙᴏᴛ ꜱᴛᴀʀᴛ\n│ /menu    → ᴍᴇɴᴜ\n│ /help    → ᴄᴏᴍᴍᴀɴᴅꜱ\n│ /redeem  → ᴄʀᴇᴅɪᴛ ᴄᴏᴅᴇ\n│ /premium → ᴩʀᴇᴍɪᴜᴍ ᴄᴏᴅᴇ\n│ /spin    → ᴅᴀɪʟʏ ꜱᴘɪɴ\n╰─────────────────╯\n\n╭─── 📱 <b>NUMBER INFO</b> ───╮\n│ /numinfo <code>9876543210</code>\n│ → ɴᴀᴍᴇ, ᴏᴩᴇʀᴀᴛᴏʀ, ꜱɪᴍ\n╰──────────────────────╯\n\n╭─── 👤 <b>USER INFO</b> ───╮\n│ /usernum <code>@username</code>\n│ /usernum <code>123456789</code>\n╰────────────────────╯\n\n╭─── 📸 <b>INSTAGRAM</b> ───╮\n│ /insta <code>username</code>\n╰─────────────────────╯\n\n╭─── 🎮 <b>FREE FIRE</b> ───╮\n│ /ffinfo <code>uid</code>\n│ /like <code>uid</code> | /like <code>ind uid</code>\n╰────────────────────╯\n\n╭─── 💣 <b>BOMBER</b> ───╮\n│ /bomb <code>9876543210</code>\n│ /stopbomb\n╰──────────────────╯\n\n╭─── ⚡ <b>AUTO DETECT</b> ───╮\n│ <code>9876543210</code> → 📱 ɴᴜᴍ\n│ <code>@username</code>  → 👤 ᴜꜱᴇʀ\n╰──────────────────────╯\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n💀 ᴅᴇᴠᴇʟᴏᴩᴇʀ : @notCoder2006</blockquote>'
    bot.reply_to(msg, txt, parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text in [' MAIN MENU', ' ᴍᴀɪɴ ᴍᴇɴᴜ', 'ᴍᴀɪɴ ᴍᴇɴᴜ', 'MAIN MENU'] and m.chat.type == 'private')
def go_main(m):
    uid = m.from_user.id
    if check_blocked_and_reply(uid):
        return
    user_state[uid] = S_NONE
    user = get_user(uid)
    nm = user[2] if user else 'User'
    un = user[1] if user else ''
    cr = get_credits(uid)
    cr_disp = '∞' if is_admin(uid) else str(cr)
    try:
        _bot_owner_un = f'@{_get_bot_username()}'
    except:
        _bot_owner_un = '@notCoder2006'
    if False:
        txt = f"<blockquote>━━━━━━━━━━━\n🤖 NORMAL ᴍᴀɪɴ ᴍᴇɴᴜ\n━━━━━━━━━━━\n💰 ᴄʀᴇᴅɪᴛꜱ: <b>{cr_disp}</b>\n━━━━━━━━━━━\n👨\u200d💻 ᴅᴇᴠ : <a href='tg://user?id={OWNER_ID}'>Owner</a></blockquote>"
    else:
        txt = f'<blockquote>⬇️ ᴍᴀɪɴ ᴍᴇɴᴜ\n💰 ᴄʀᴇᴅɪᴛꜱ: <b>{cr_disp}</b>\n⚡ {_bot_owner_un}</blockquote>'
    bot.send_message(uid, txt, reply_markup=kb_p1(uid), parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text == ' ᴄᴀɴᴄʟᴇ' and m.chat.type == 'private')
def h_cancle(m):
    uid = m.from_user.id
    if check_blocked_and_reply(uid):
        return
    user_state[uid] = S_NONE
    bot.send_message(uid, '<blockquote>⬇ ᴍᴀɪɴ ᴍᴇɴᴜ</blockquote>', reply_markup=kb_p1(uid), parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text in [' CANCEL', ' ᴄᴀɴᴄᴇʟ'])
def go_cancel(m):
    uid = m.from_user.id
    user_state[uid] = S_NONE
    bot.send_message(uid, '<blockquote>⬇ ᴍᴀɪɴ ᴍᴇɴᴜ</blockquote>', reply_markup=kb_p1(uid), parse_mode='HTML')

def feat_ok(uid, fn, chat_id=None):
    if check_blocked_and_reply(uid):
        return False
    target = chat_id if chat_id else uid
    if (not _MAIN_BOT_ACTIVE) and (not is_admin(uid)):
        bot.send_message(target, '<blockquote> <b>ʙᴏᴛ ᴏꜰꜰʟɪɴᴇ</b>\nBot abhi maintenance mode mein hai.\nThodi der baad try karo.\n @notCoder2006</blockquote>', parse_mode='HTML')
        return False
    if not is_feature_enabled(fn):
        bot.send_message(target, f'<blockquote>━━━━━━━━━━━━━━━━━━\n⚙️ ᴛʜɪꜱ ꜰᴇᴀᴛᴜʀᴇ ɪꜱ ᴜɴᴅᴇʀ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ\n━━━━━━━━━━━━━━━━━━\n🛠️ ʜᴀᴍ ɪꜱ ꜰᴇᴀᴛᴜʀᴇ ᴋᴏ ᴀᴩᴅᴀᴛᴇ ᴋᴀʀ ʀᴀʜᴇ ʜᴀɪɴ\n📝 ᴄᴀᴜꜱᴇ: 🔧 System maintenance\n⏳ ᴛʜᴏᴅɪ ᴅᴇʀ ᴍᴇɪɴ ᴡᴀᴩᴀꜱ ᴀᴀ ᴊᴀᴇɢᴀ!\n━━━━━━━━━━━━━━━━━━\n💀 ᴅᴇᴠᴇʟᴏᴩᴇʀ : @notCoder2006</blockquote>', parse_mode='HTML')
        return False
    return True

@bot.message_handler(func=lambda m: m.text in ['ɴᴜᴍʙᴇʀ ɪɴꜰᴏ', ' NUMBER INFO', 'ɴᴜᴍʙᴇʀ ɪɴꜰᴏ', 'ɴᴜᴍʙᴇʀ ɪɴꜰᴏ', 'ɴᴜᴍʙᴇʀ ɪɴꜰᴏ'])
def h_num(m):
    uid = m.from_user.id
    if not feat_ok(uid, 'number'):
        return
    user_state[uid] = S_NUM
    _cr = get_credits(uid)
    try:
        bn = _get_bot_username()
    except:
        bn = 'bot'

    def te(eid, fb='⭐'):
        return f"{fb}"
    e_loop = te('5465270065102334742', '')
    e_phone = te('5193178118759660952', '')
    e_gift1 = te('5384544226333711035', '')
    e_gift2 = te('5462982187563380518', '')
    e_bot = te('5355051922862653659', '')
    e_star = te('6118385795976930086', '')
    L12 = e_loop * 12
    bot.reply_to(m, f'<blockquote>{L12}\n{e_phone} <b>𝗡𝗨𝗠𝗕𝗘𝗥 𝗜𝗡𝗙𝗢</b>\n{L12}\n\nSᴇɴᴅ 10-ᴅɪɢɪᴛ Mᴏʙɪʟᴇ Nᴜᴍʙᴇʀ\nExᴀᴍᴩʟᴇ :- <code>9876543210</code>\n\n{e_gift1}Tᴏᴛᴀʟ :- <b>{_cr}</b> Cʀᴇᴅɪᴛ\n{e_gift2}Pᴇʀ-Uꜱᴇ :- <b>01</b> Cʀᴇᴅɪᴛ\n{L12}\n{e_bot} Pᴏᴡᴇʀᴇᴅ Bʏ: @{bn}  {e_star}\n{L12}</blockquote>', parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text in [' SELECT USER', 'ꜱᴇʟᴇᴄᴛ ᴜꜱᴇʀ', 'ꜱᴇʟᴇᴄᴛ ᴜꜱᴇʀ', ''])
def h_sel(m):
    uid = m.from_user.id
    if check_blocked_and_reply(uid):
        return
    user_state[uid] = S_USER

@bot.message_handler(func=lambda m: m.text in [' ᴜꜱᴇʀɴᴀᴍᴇ ᴛᴏ ɴᴜᴍ', ' USERNAME INFO', ' ᴜꜱᴇʀɴᴀᴍᴇ ɪɴꜰᴏ', 'ᴜꜱᴇʀɴᴀᴍᴇ ᴛᴏ ɴᴜᴍ', 'ᴛɢ ᴜꜱᴇʀ ᴛᴏ ɴᴜᴍ', 'ᴛɢ ᴛᴏ ɴᴜᴍ', 'TG TO NUM'])
def h_user(m):
    uid = m.from_user.id
    if not feat_ok(uid, 'username'):
        return
    user_state[uid] = S_USER
    _cr = get_credits(uid)

    def _te(*args, **kwargs): return ""
    _L = _te('5465270065102334742') * 10
    bot.reply_to(m, f"<blockquote>{_L}\n{_te('5188217332748527444')} 𝗧𝗚 𝗧𝗢 𝗡𝗨𝗠\n{_L}\n\nSᴇɴᴅ @username ʏᴀ TG ID\nEᴇxᴀᴍᴩʟᴇ :- <code>@durov</code> ʏᴀ <code>123456789</code>\n\nTɪᴩ: ʏᴏᴜ ᴄᴀɴ ꜰɪɴᴅ ᴜꜱᴇʀ ɪᴅ ᴜꜱɪɴɢ @userinfobot\n\n{_te('5384544226333711035')} Tᴏᴛᴀʟ :- <b>{_cr} Cʀᴇᴅɪᴛ</b>\n{_te('5462982187563380518')} Pᴇʀ-Uꜱᴇ :- <b>01 Cʀᴇᴅɪᴛ</b>\n{_L}\n{_te('5355051922862653659')} Pᴏᴡᴇʀᴇᴅ Bʏ: @{_get_bot_username()} {_te('6118385795976930086')}\n{_L}</blockquote>", parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text in [' ᴛɢ ɪᴅ ᴛᴏ ɴᴜᴍ', ' TG ID INFO', ' ᴛɢ ɪᴅ ɪɴꜰᴏ', 'ᴛɢ ɪᴅ ᴛᴏ ɴᴜᴍ'])
def h_tid(m):
    uid = m.from_user.id
    if not feat_ok(uid, 'tgid'):
        return
    user_state[uid] = S_TID
    _cr = get_credits(uid)

    def _te(*args, **kwargs): return ""
    _L = _te('5465629669829128119') * 12
    bot.reply_to(m, f"<blockquote>{_L}\n{_te('5888620056551625531')} <b>𝗧𝗚 𝗜𝗗 𝗧𝗢 𝗡𝗨𝗠𝗕𝗘𝗥</b>\n{_L}\n\n{_te('5258362837411045098')} ꜱᴇɴᴅ <b>Telegram User ID</b>\nᴇxᴀᴍᴩʟᴇ: <code>123456789</code>\n\n{_te('5472146462362048818')} ᴛɪᴩ: ʏᴏᴜ ᴄᴀɴ ɢᴇᴛ ɪᴅ ꜰʀᴏᴍ @userinfobot\n\n{_te('5224257782013769471')} Tᴏᴛᴀʟ Pᴏɪɴᴛ :- <b>{_cr} Pᴏɪɴᴛ</b>\n{_te('5188311512791393083')} Sᴇᴀʀᴄʜ Cᴏꜱᴛ :- <b>1 Pᴏɪɴᴛ</b>\n\n{_te('6204263190319081111')} ʙᴏᴛ ᴍᴀᴅᴇ ʙʏ : @notCoder2006 {_te('6147565374289220368')}</blockquote>", parse_mode='HTML')

def _is_aadhar_btn(m):
    if not m.text or m.chat.type != 'private':
        return False
    t = m.text.strip()
    keys = [' AADHAR INFO', ' ', '', 'AADHAR INFO', 'aadhar info', 'AADHAR']
    if t in keys:
        return True
    tl = t.lower().replace(' ', '')
    if 'aadhar' in tl or 'ᴀᴀᴅʜᴀʀ' in t or 'adhaar' in tl:
        if 'admin' in tl or 'toggle' in tl:
            return False
        return True
    return False

def _do_group_spin(uid, fname, uname_tg, cid):
    """Group spin logic — anyone can call, handles cooldown, sends result to cid"""
    try:
        user = get_user(uid)
        if not user:
            add_user(uid, uname_tg, fname)
            user = get_user(uid)
        FS = _SEP()
        if not (is_admin(uid) or can_claim_daily(uid)):
            bot.send_message(cid, f"<blockquote>{FS}\n⏰ <a href='tg://user?id={uid}'><b>{fname}</b></a>\n❌ Aaj ka spin already le chuke ho!\n🕐 Kal wapis aao!\n{FS}\n⚡ @notCoder2006</blockquote>", parse_mode='HTML')
            return
        dm = bot.send_dice(cid, emoji=_get_spin_emoji())
        time.sleep(5)
        cw = {1: 1, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5}.get(dm.dice.value, 1)
        c.execute('UPDATE users SET credits=credits+? WHERE user_id=?', (cw, uid))
        conn.commit()
        if not is_admin(uid):
            c.execute('INSERT OR IGNORE INTO daily_claims VALUES(?,?)', (uid, datetime.now().strftime('%Y-%m-%d')))
            conn.commit()
        user_obj = get_user(uid)
        tot = user_obj[5] if user_obj else cw
        try:
            bn2 = _get_bot_username()
        except:
            bn2 = '𝙽𝚘𝚝 𝙲𝚘𝚍𝚎𝚛_bot'
        log_token_activity(uid, fname, uname_tg, cw, tot, 'Daily Spin', bn2)
        bot.send_message(cid, f"<blockquote>{FS}\n🎯 <b>ᴅᴀɪʟʏ ꜱᴩɪɴ</b>\n{FS}\n\n<a href='tg://user?id={uid}'><b>{fname}</b></a> ne spin kiya!\n\n🎉 Won: <code>+{cw}</code> credits!\n💰 Total: <code>{tot}</code>\n\n{FS}\n⚡ @notCoder2006</blockquote>", parse_mode='HTML')
    except Exception as _spin_e:
        print(f'[SPIN_ERR] {_spin_e}')

@bot.message_handler(func=lambda m: m.text in [' DAILY SPIN', ' ᴅᴀɪʟʏ ꜱᴘɪɴ', ' ᴅᴀɪʟʏ ꜱᴘɪɴ', 'ᴅᴀɪʟʏ ꜱᴘɪɴ', 'ᴅᴀɪʟʏ ꜱᴘɪɴ'])
def h_spin(m):
    uid = m.from_user.id
    if check_blocked_and_reply(uid):
        return
    if is_admin(uid) or can_claim_daily(uid):
        dm = bot.send_dice(uid, emoji=_get_spin_emoji())
        time.sleep(5)
        cw = {1: 1, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5}.get(dm.dice.value, 1)
        c.execute('UPDATE users SET credits=credits+? WHERE user_id=?', (cw, uid))
        if not is_admin(uid):
            c.execute('INSERT OR IGNORE INTO daily_claims VALUES(?,?)', (uid, datetime.now().strftime('%Y-%m-%d')))
        conn.commit()
        _user_cache.pop(uid, None)
        user = get_user(uid)
        tot = user[5] if user else cw
        _SS = _SEP()
        _SE = _SEP()
        _spin_ref2 = f'https://t.me/{_get_bot_username()}?start={uid}'
        _spin_vp2 = _spin_ref2
        _spin_mk2 = InlineKeyboardMarkup()

        def _te(*args, **kwargs): return ""
        _L2 = _te('5465629669829128119') * 11
        _spin_mk2.add(_IKB(f'ꜱʜᴀʀᴇ — +{get_referral_bonus()} ᴄʀᴇᴅɪᴛ ᴩᴀᴏ', style='success', url='https://t.me/share/url?url=' + _spin_vp2 + '&text=Yaar+is+bot+ko+join+karo+aur+free+credits+pao!'))
        _spin_mk2.add(_IKB('ᴍʏ ᴄʀᴇᴅɪᴛꜱ ᴅᴇᴋʜᴏ', style='primary', callback_data='show_my_credits'))
        bot.send_message(uid, f"<blockquote>{_L2}\n{_te('6242498410822244114')} ᴅᴀɪʟʏ ꜱᴘɪɴ\n{_L2}\n{_te('5219745609631674840')} Wᴏɴ: <code>+{cw}</code> ᴄʀᴇᴅɪᴛꜱ\n{_te('5224257782013769471')} Tᴏᴛᴀʟ: <b>{tot}</b>\n{_L2}\n{_te('6204263190319081111')} ʙᴏᴛ ᴍᴀᴅᴇ ʙʏ : @notCoder2006 {_te('6147565374289220368')}</blockquote>", reply_markup=_spin_mk2, parse_mode='HTML')
        try:
            bn = _get_bot_username()
        except:
            bn = '𝙽𝚘𝚝 𝙲𝚘𝚍𝚎𝚛_bot'
        log_token_activity(uid, m.from_user.first_name or 'User', m.from_user.username or '', cw, tot, 'Daily Spin', bn)
    else:
        bot.reply_to(m, '<blockquote> Already claimed today!\n Come back tomorrow!\n @notCoder2006</blockquote>', parse_mode='HTML')

def _is_refer_btn(m):
    if not m.text or m.chat.type != 'private':
        return False
    t = m.text.strip()
    tl = t.lower().replace(' ', '')
    if t in ('ʀᴇꜰᴇʀʀᴀʟ ꜱᴇᴛᴛɪɴɢ', 'ʀᴇꜰᴇʀʀᴀʟ ʙᴏɴᴜꜱ') and is_admin(m.from_user.id):
        return False
    keys = ['ʀᴇꜰᴇʀ & ᴇᴀʀɴ', 'refer & earn', 'refer&earn', 'ʀᴇꜰᴇʀ&ᴇᴀʀɴ', 'ᴡᴀʟʟᴇᴛ & ʀᴇꜰᴇʀ', 'wallet & refer', 'referrals', 'ʀᴇꜰᴇʀʀᴀʟꜱ', 'get refer point', 'ɢᴇᴛ ʀᴇꜰᴇʀ ᴩᴏɪɴᴛ']
    if t in keys or tl in [k.lower().replace(' ', '') for k in keys]:
        return True
    if 'ʀᴇꜰᴇʀ' in t or 'refer' in tl or 'ᴇᴀʀɴ' in t:
        if 'admin' in tl or 'panel' in tl:
            return False
        return True
    return False

@bot.message_handler(func=_is_refer_btn)
def h_ref(m):
    uid = m.from_user.id
    try:
        if check_blocked_and_reply(uid):
            return
    except:
        pass
    cnt = get_referral_count(uid)
    try:
        bn = _get_bot_username()
        lnk = f'https://t.me/{bn}?start={uid}'
    except:
        lnk = f'https://t.me/bot?start={uid}'
    total_earn = int(cnt) * int(get_referral_bonus())

    def _te(*args, **kwargs): return ""
    _L11 = _te('5465270065102334742', '') * 11
    _L6 = _te('5465270065102334742', '') * 6
    mk = InlineKeyboardMarkup()
    mk.row(_IKB('ꜱʜᴀʀᴇ ʟɪɴᴋ', style='success', url=f'https://t.me/share/url?url={lnk}&text=Join+this+amazing+info+bot!'), _IKB('ʙᴜʏ ᴄʀᴇᴅɪᴛꜱ', style='primary', callback_data='show_premium_plans'))
    bot.reply_to(m, f"<blockquote>{_L11}\n{_te('6267068789146260253', '')} 𝗥𝗲𝗳𝗲𝗿 & 𝗲𝗮𝗿𝗻 {_te('6001078118725456537', '')}\n{_L11}\n\n{_te('5406809207947142040', '')} ᴛᴏᴛᴀʟ ʀᴇꜰᴇʀꜱ : <b>{cnt}</b> Fʀɪᴇɴᴅꜱ\n{_te('6089104607328342288', '')} Tᴏᴛᴀʟ Eᴀʀɴ :- <b>{total_earn}</b> Cʀᴇᴅɪᴛ\n\n{_L6}\n{_te('5983262173474853675', '')} ʏᴏᴜʀ ʀᴇꜰᴇʀʀᴀʟ ʟɪɴᴋ:\n<code>{lnk}</code>\n\n{_L6}\n{_te('5470177992950946662', '')} Tᴀᴩ ᴛᴏ Rᴇꜰᴇʀ ᴛᴏ Fʀɪᴇɴᴅ {_te('5213395028038132311', '')}:</blockquote>", reply_markup=mk, parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text in [' MY CREDITS', ' ᴍʏ ᴄʀᴇᴅɪᴛꜱ', 'ᴍʏ ᴄʀᴇᴅɪᴛꜱ', 'MY CREDITS', 'my credits', 'ᴍʏ ᴄʀᴇᴅɪᴛꜱ', 'ᴡᴀʟʟᴇᴛ & ʀᴇꜰᴇʀ'] or (m.text and 'MY CREDITS' in m.text.upper() and (m.chat.type == 'private')))
def h_credits(m):
    uid = m.from_user.id
    if check_blocked_and_reply(uid):
        return
    cr = get_credits(uid)
    refs = get_referral_count(uid)
    user = get_user(uid)
    is_prem = bool(user[8]) if user else False
    prem_str = ' ᴜɴʟɪᴍɪᴛᴇᴅ' if is_prem else f'{cr}'
    spin_done = not can_claim_daily(uid)
    spin_str = ' ᴄʟᴀɪᴍᴇᴅ' if spin_done else ' ᴀᴠᴀɪʟᴀʙʟᴇ'
    try:
        rl = f'https://t.me/{_get_bot_username()}?start={uid}'
    except:
        rl = '--'
    rl_short = rl
    show_v = False
    mk = InlineKeyboardMarkup(row_width=2)
    mk.row(_IKB('ꜱʜᴀʀᴇ ʟɪɴᴋ', style='success', url=f'https://t.me/share/url?url={rl_short}&amp;text=Join+karo!'), _IKB('ɢᴇᴛ ᴀᴄᴄᴇꜱꜱ', style='primary', callback_data='show_premium_plans'))

    def te(eid, fb='⭐'):
        return f"{fb}"
    e_loop = te('5465270065102334742', '')
    e_money = te('6267068789146260253', '')
    e_chain = te('6001078118725456537', '')
    e_phone = te('5406809207947142040', '')
    e_coin = te('6089104607328342288', '')
    e_link = te('5983262173474853675', '')
    e_down = te('5470177992950946662', '')
    e_ok = te('5213395028038132311', '')
    L11 = e_loop * 11
    L6 = e_loop * 6
    try:
        total_earn = int(refs) * int(get_referral_bonus())
    except Exception:
        total_earn = 0
    _cr_txt = f'<blockquote>{L11}\n{e_money} <b>𝗥𝗲𝗳𝗲𝗿 & 𝗲𝗮𝗿𝗻</b> {e_chain}\n{L11}\n\n{e_phone} ᴛᴏᴛᴀʟ ʀᴇꜰᴇʀꜱ : <b>{refs}</b> Fʀɪᴇɴᴅꜱ\n{e_coin} Tᴏᴛᴀʟ Eᴀʀɴ :- <b>{total_earn}</b> Cʀᴇᴅɪᴛ\n\n{L6}\n{e_link} ʏᴏᴜʀ ʀᴇꜰᴇʀʀᴀʟ ʟɪɴᴋ:\n<code>{rl_short}</code>\n\n{L6}\n{e_down} Tᴀᴩ ᴛᴏ Rᴇꜰᴇʀ ᴛᴏ Fʀɪᴇɴᴅ {e_ok}:</blockquote>'
    try:
        bot.reply_to(m, _cr_txt, reply_markup=mk, parse_mode='HTML')
    except Exception as _hcr_e:
        try:
            bot.send_message(m.chat.id, _cr_txt, reply_markup=mk, parse_mode='HTML')
        except Exception as _hcs_e:
            print(f'[H_CREDITS] {_hcs_e}')

@bot.message_handler(func=lambda m: m.text in [' ʀᴇᴅᴇᴇᴍ ᴄᴏᴅᴇ', ' REDEEM CODE', 'ʀᴇᴅᴇᴇᴍ ᴄᴏᴅᴇ', 'ʀᴇᴅᴇᴇᴍ ᴄᴏᴅᴇ'])
def h_redeem(m):
    uid = m.from_user.id
    if check_blocked_and_reply(uid):
        return
    mk = InlineKeyboardMarkup(row_width=1)
    mk.add(_IKB(' ʀᴇᴅᴇᴇᴍ ᴄʀᴇᴅɪᴛ ᴄᴏᴅᴇ', style='success', callback_data='redeem_credit_code'))
    mk.add(_IKB(' ʀᴇᴅᴇᴇᴍ ᴘʀᴇᴍɪᴜᴍ ᴄᴏᴅᴇ', style='primary', callback_data='redeem_premium_code'))
    bot.reply_to(m, f'<blockquote>{_CL_TOP()}\n│  🎫 <b>ʀᴇᴅᴇᴇᴍ ᴄᴏᴅᴇ</b>\n{_CL_BOT()}\n\n🎫 Credit Code: <code>NOT_CODER-XXXXXX</code>\n💎 Premium Code: <code>NOT_CODER_PR-XXXXXX</code>\n\nKaunsa code redeem karna hai?\n\n{_F}\n⚡ @notCoder2006</blockquote>', reply_markup=mk, parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text in ['ℹ HELP', 'ℹ ʜᴇʟᴩ', 'ʜᴇʟᴩ', 'ʜᴇʟᴩ'])
def h_help(m):
    uid = m.from_user.id
    if check_blocked_and_reply(uid):
        return
    _sep = '━━━━━━━━━━━━━━━━━━'

    def _te(*args, **kwargs): return ""
    _L = _te('5465629669829128119') * 10
    txt = f"<blockquote>{_L}\n{_te('5197269100878907942')} <b>ʜᴇʟᴩ — ᴄᴏᴍᴍᴀɴᴅꜱ</b>\n{_sep}\n\n{_te('5888781182249738113')} <b>INFO LOOKUP</b>\n{_te('5431577498364158238')} Number Info — Indian number details\n{_te('5888781182249738113')} TG ID Info — Telegram user by ID\n{_te('5373012449597335010')} Username Info — TG user by @username\n{_te('5373012449597335010')} Select User — share contact\n{_te('5888781182249738113')} Aadhar Info\n{_te('5470135030393090150')} Instagram Info\n{_te('5888781182249738113')} Vehicle Info\n{_te('5888781182249738113')} PAN Info\n{_te('5431577498364158238')} Pak Number Info\n\n{_te('5406631276042002796')} <b>FREE FIRE</b>\n{_te('4958734459869332468')} FF Info — player stats + outfit\n{_te('5372926953978341366')} FF Like — send likes to UID\n\n{_te('5888781182249738113')} <b>BOMBER</b>\n/bomb [10-digit number]\n/stopbomb — stop running bomber\n\n{_te('5888781182249738113')} <b>GROUP COMMANDS</b>\n/spin — Daily spin\n/like [region] [uid] — FF like\n/info [uid] — FF player info\n/user [userid] — TG user info\n\n{_te('4958734459869332468')} <b>CREDITS</b>\n{_te('5197269100878907942')} Daily Spin — earn credits\n{_te('5465300082628763143')} Refer friends — earn credits\n/redeem [code] — redeem code\n\n\n{_sep}\n1 cr/search | FF Like=2cr | Bomber=4cr\n{_L}\n{_te('6147464060305676048')} @notCoder2006 {_te('6147565374289220368')}\n{_te('5888781182249738113')} ᴏᴡɴᴇʀ: @notCoder2006\n{_L}</blockquote>"


@bot.message_handler(func=lambda m: m.text in [' OWNER', ' ᴏᴡɴᴇʀ', ' ᴏᴡɴᴇʀ', 'ᴏᴡɴᴇʀ', 'ꜱᴜᴩᴩᴏʀᴛ'])
def h_owner(m):
    if check_blocked_and_reply(m.from_user.id):
        return

    def _te(*args, **kwargs): return ""
    _L = _te('5465629669829128119') * 10
    _SM = _te('6147464060305676048')
    _CK = _te('6147565374289220368')
    _Crown = _te('6289741869962236795')
    _Star = _te('5465629669829128119')
    mk = InlineKeyboardMarkup()
    mk.add(_IKB(' Contact @notCoder2006', url='https://t.me/LUFFY_49'))
    mk.add(_IKB(' Join @notCoder2006', url='https://t.me/𝙽𝚘𝚝 𝙲𝚘𝚍𝚎𝚛'))
    bot.reply_to(m, f'<blockquote>{_L}\n{_Crown} <b>ᴏᴡɴᴇʀ / ꜱᴜᴩᴩᴏʀᴛ</b>\n\nɪꜰ ʏᴏᴜ ꜰᴀᴄᴇ ᴀɴʏ ɪꜱꜱᴜᴇꜱ, ᴄᴏɴᴛᴀᴄᴛ ᴏᴜʀ ᴀᴅᴍɪɴ:\n🌐 @notCoder2006\n⭐ 5908171064\n\n{_L}\n{_SM} @notCoder2006 {_CK}\n{_L}</blockquote>', reply_markup=mk, parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text in [' LEADERBOARD', ' ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ', 'ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ', 'ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ'])
def h_leaderboard(m):
    uid = m.from_user.id
    if check_blocked_and_reply(uid):
        return
    today = datetime.now()
    week_start = (today - timedelta(days=today.weekday())).strftime('%Y-%m-%d')
    rows = c.execute('SELECT u.user_id,u.first_name,u.username,COUNT(r.id) as cnt FROM users u LEFT JOIN referrals r ON u.user_id=r.referrer AND r.date >= ? GROUP BY u.user_id ORDER BY cnt DESC LIMIT 10', (week_start,)).fetchall()

    def _te(*args, **kwargs): return ""
    LOOP = _te('5465629669829128119') * 12
    TROPHY = _te('5409008750893734809')
    WIN_TROPHY = _te('5886579736632629397')
    DEV_EMOJI = _te('6147464060305676048')
    CHECK_EMOJI = _te('6147565374289220368')
    num_emojis = ['6269400956387987689', '5447203607294265305', '5453902265922376865', '6219826747345471627', '6219909202127620214', '6221746649266391336', '6220028211376425519', '6222219718439209089', '6222084349659973777', '5312157624915999161']
    top1 = rows[0] if rows else None
    top1_disp = ''
    if top1:
        top1_disp = f'@{top1[2]}' if top1[2] else (top1[1] or 'User')[:15]
    txt = f'{LOOP}\n\n{TROPHY} ᴡᴇᴇᴋʟʏ ʀᴇꜰᴇʀʀᴀʟ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ\n\n{LOOP}\n\n'
    if today.weekday() == 6 and top1 and (top1[3] > 0):
        txt += f'{WIN_TROPHY} {top1_disp} ᴡᴏɴ 3ᴅᴀʏꜱ ᴩʀᴇᴍɪᴜᴍ !!\n\n'
        try:
            until = (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S')
            c.execute('UPDATE users SET is_premium=1,premium_until=? WHERE user_id=?', (until, top1[0]))
            conn.commit()
        except:
            pass
    for i, (ruid, fname, uname, cnt) in enumerate(rows):
        disp = f'@{uname}' if uname else (fname or 'User')[:15]
        eid = num_emojis[i] if i < len(num_emojis) else '6219826747345471627'
        you = ' ← ʏᴏᴜ' if ruid == uid else ''
        rw = 'refs' if cnt != 1 else 'ref'
        txt += f'{_te(eid)} {disp} — {cnt} {rw}{you}\n'
    bot.reply_to(m, f'<blockquote>{txt}</blockquote>', parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text in [' ᴏꜰꜰ ᴍʏ ʙᴏᴛ', ' ᴏɴ ᴍʏ ʙᴏᴛ'] and is_admin(m.from_user.id))
def h_toggle_main_bot(m):
    """Original bot ka ON/OFF toggle — sirf main owner (admin panel pe)"""
    global _MAIN_BOT_ACTIVE
    uid = m.from_user.id
    if uid != OWNER_ID:
        bot.reply_to(m, '<blockquote> Sirf main owner use kar sakta hai!</blockquote>', parse_mode='HTML')
        return
    _MAIN_BOT_ACTIVE = not _MAIN_BOT_ACTIVE
    status_icon = '' if _MAIN_BOT_ACTIVE else ''
    status_text = 'ON — Bot ab responses dega!' if _MAIN_BOT_ACTIVE else 'OFF — Bot silent mode mein!'
    bot.reply_to(m, f'<blockquote>{_F}\n   {status_icon} <b>ᴍᴀɪɴ ʙᴏᴛ ꜱᴛᴀᴛᴜꜱ</b>\n{_F}\n\nStatus: <b>{status_text}</b>\n\n{_F}\n⚡ @notCoder2006</blockquote>', reply_markup=kb_admin_p1(), parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text in [' ADMIN PANEL', ' ᴀᴅᴍɪɴ ᴩᴀɴᴇʟ', 'ᴀᴅᴍɪɴ ᴩᴀɴᴇʟ'] and is_admin(m.from_user.id))
def h_admin(m):
    user_state[m.from_user.id] = 'ADMIN_PANEL'
    bot.send_message(m.chat.id, '<blockquote> <b>ᴀᴅᴍɪɴ ᴩᴀɴᴇʟ P1</b></blockquote>', reply_markup=kb_admin_p1(), parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text in [' ADMIN PAGE 2', 'ADMIN PAGE 2', 'ᴀᴅᴍɪɴ ᴩᴀɢᴇ 2'] and is_admin(m.from_user.id))
def h_adp2(m):
    bot.send_message(m.chat.id, '<blockquote> <b>Admin P2</b></blockquote>', reply_markup=kb_admin_p2(), parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text in ['⬅ ADMIN PAGE 1', '⬅ ᴀᴅᴍɪɴ ᴩᴀɢᴇ 1', 'ᴀᴅᴍɪɴ ᴩᴀɢᴇ 1'] and is_admin(m.from_user.id))
def h_adp1b(m):
    bot.send_message(m.chat.id, '<blockquote> <b>Admin P1</b></blockquote>', reply_markup=kb_admin_p1(), parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text in ['ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴍᴇɴᴜ', 'BROADCAST MENU'] and is_admin(m.from_user.id))
def h_bc_menu(m):
    mk = InlineKeyboardMarkup()
    mk.row(_IKB(' All Users', style='primary', callback_data='adm_bc_all'))
    mk.row(_IKB(' Premium Only', style='success', callback_data='adm_bc_prem'))
    mk.row(_IKB(' Schedule BC', style='primary', callback_data='adm_bc_sched'))
    bot.reply_to(m, '<blockquote> <b>BROADCAST MENU</b>\nSelect type:</blockquote>', reply_markup=mk, parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text in ['ʀᴇᴅᴇᴇᴍ ᴍᴇɴᴜ', 'REDEEM MENU'] and is_admin(m.from_user.id))
def h_redeem_menu(m):
    mk = InlineKeyboardMarkup()
    mk.row(_IKB(' Normal Redeem Code', style='success', callback_data='adm_gen_redeem'))
    mk.row(_IKB(' Premium Redeem Code', style='primary', callback_data='adm_gen_premium'))
    bot.reply_to(m, '<blockquote> <b>REDEEM MENU</b>\nSelect code type:</blockquote>', reply_markup=mk, parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text in ['ᴄʀᴇᴅɪᴛꜱ ᴍᴇɴᴜ', 'CREDITS MENU'] and is_admin(m.from_user.id))
def h_credits_menu(m):
    mk = InlineKeyboardMarkup()
    mk.row(_IKB(' Add Credits', style='success', callback_data='adm_add_cr'))
    mk.row(_IKB(' Remove Credits', style='danger', callback_data='adm_rem_cr'))
    mk.row(_IKB(' Check Credits', style='primary', callback_data='adm_chk_cr'))
    bot.reply_to(m, '<blockquote> <b>CREDITS MENU</b>\nSelect action:</blockquote>', reply_markup=mk, parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text in ['ᴩʀᴇᴍɪᴜᴍ ᴍᴇɴᴜ', 'PREMIUM MENU'] and is_admin(m.from_user.id))
def h_prem_menu(m):
    mk = InlineKeyboardMarkup()
    mk.row(_IKB(' Gen Premium Code', style='success', callback_data='adm_gen_premium'))
    mk.row(_IKB(' Add Premium (UID)', style='primary', callback_data='adm_add_prem'))
    mk.row(_IKB(' Remove Premium', style='danger', callback_data='adm_rem_prem'))
    mk.row(_IKB(' Revoke All Premium', style='danger', callback_data='adm_revoke_all'))
    bot.reply_to(m, '<blockquote> <b>PREMIUM MENU</b>\nSelect action:</blockquote>', reply_markup=mk, parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text in ['ᴀᴅᴍɪɴ ᴍᴇɴᴜ', 'ADMIN MENU'] and is_admin(m.from_user.id))
def h_admin_menu(m):
    user_state[m.from_user.id] = 'ADMIN_ADMIN_MGMT'
    bot.send_message(m.chat.id, '<blockquote> <b>Admin Mgmt</b></blockquote>', reply_markup=kb_admin_mgmt(), parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text in ['ᴄʜᴀɴɴᴇʟ ᴍᴇɴᴜ', 'CHANNEL MENU'] and is_admin(m.from_user.id))
def h_channel_menu(m):
    user_state[m.from_user.id] = 'ADMIN_CHANNEL_MGMT'
    bot.send_message(m.chat.id, '<blockquote> <b>Channel Mgmt</b></blockquote>', reply_markup=kb_channel_mgmt(), parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text in ['ɢʀᴏᴜᴩ ᴍᴇɴᴜ', 'GROUP MENU'] and is_admin(m.from_user.id))
def h_group_menu(m):
    mk = InlineKeyboardMarkup()
    mk.row(_IKB(' Group Management', style='primary', callback_data='adm_grp_mgmt'))
    mk.row(_IKB(' Group Control', style='primary', callback_data='adm_grp_ctrl'))
    bot.reply_to(m, '<blockquote> <b>GROUP MENU</b>\nSelect:</blockquote>', reply_markup=mk, parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text in ['ᴡᴇʟᴄᴏᴍᴇ ᴍᴇɴᴜ', 'WELCOME MENU'] and is_admin(m.from_user.id))
def h_welcome_menu(m):
    mk = InlineKeyboardMarkup()
    mk.row(_IKB(' Bot Welcome', style='primary', callback_data='adm_bot_welcome'))
    mk.row(_IKB(' Group Welcome', style='primary', callback_data='adm_grp_welcome'))
    bot.reply_to(m, '<blockquote> <b>WELCOME MENU</b>\nSelect:</blockquote>', reply_markup=mk, parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text in ['ᴀᴩɪ ᴍᴇɴᴜ', 'API MENU'] and is_admin(m.from_user.id))
def h_api_menu(m):
    mk = InlineKeyboardMarkup()
    mk.row(_IKB(' API URLs', style='primary', callback_data='adm_api_urls'))
    mk.row(_IKB(' API Keys', style='primary', callback_data='adm_api_keys'))
    bot.reply_to(m, '<blockquote> <b>API MENU</b>\nSelect:</blockquote>', reply_markup=mk, parse_mode='HTML')

@bot.callback_query_handler(func=lambda c: c.data and c.data.startswith('adm_') and is_admin(c.from_user.id))
def cb_admin_menus(call):
    d = call.data
    uid = call.from_user.id
    try:
        bot.answer_callback_query(call.id)
    except:
        pass
    if d == 'adm_bc_all':
        bot.send_message(uid, '<blockquote> Send message to ALL users:</blockquote>', parse_mode='HTML')
        bot.register_next_step_handler_by_chat_id(uid, do_broadcast)
    elif d == 'adm_bc_prem':
        bot.send_message(uid, '<blockquote> Send message to PREMIUM users:</blockquote>', parse_mode='HTML')
        bot.register_next_step_handler_by_chat_id(uid, do_premium_broadcast)
    elif d == 'adm_bc_sched':
        bot.send_message(uid, '<blockquote> Format: <code>YYYY-MM-DD HH:MM | message</code></blockquote>', parse_mode='HTML')
        bot.register_next_step_handler_by_chat_id(uid, do_schedule_bc)
    elif d == 'adm_gen_redeem':
        bot.send_message(uid, '<blockquote> Send: <code>credits user_limit</code>\nExample: <code>100 5</code>\nUnlimited: <code>unlimited 10</code></blockquote>', parse_mode='HTML')
        bot.register_next_step_handler_by_chat_id(uid, do_gencode)
    elif d == 'adm_gen_premium':
        bot.send_message(uid, '<blockquote> Send: <code>days user_limit</code>\nExample: <code>30 1</code></blockquote>', parse_mode='HTML')
        bot.register_next_step_handler_by_chat_id(uid, do_gen_premium_code)
    elif d == 'adm_add_cr':
        bot.send_message(uid, '<blockquote> Send: <code>uid amount</code></blockquote>', parse_mode='HTML')
        bot.register_next_step_handler_by_chat_id(uid, do_addcr)
    elif d == 'adm_rem_cr':
        bot.send_message(uid, '<blockquote> Send: <code>uid amount</code></blockquote>', parse_mode='HTML')
        bot.register_next_step_handler_by_chat_id(uid, do_remcr)
    elif d == 'adm_chk_cr':
        bot.send_message(uid, '<blockquote> Send User ID:</blockquote>', parse_mode='HTML')
        bot.register_next_step_handler_by_chat_id(uid, do_check_cr)
    elif d == 'adm_add_prem':
        bot.send_message(uid, '<blockquote> Send: <code>uid days</code></blockquote>', parse_mode='HTML')
        bot.register_next_step_handler_by_chat_id(uid, do_prem)
    elif d == 'adm_rem_prem':
        bot.send_message(uid, '<blockquote> Send User ID to remove premium:</blockquote>', parse_mode='HTML')
        bot.register_next_step_handler_by_chat_id(uid, do_rem_prem)
    elif d == 'adm_revoke_all':
        mk = InlineKeyboardMarkup()
        mk.row(_IKB(' YES, REVOKE ALL', style='danger', callback_data='confirm_revoke_premium'), _IKB(' CANCEL', style='success', callback_data='cancel_revoke_premium'))
        bot.send_message(uid, '<blockquote>⚠️ <b>CONFIRM REVOKE ALL PREMIUM</b>\n\nThis will remove premium status and reset credits for premium users.</blockquote>', reply_markup=mk, parse_mode='HTML')
    elif d == 'adm_add_adm':
        bot.send_message(uid, '<blockquote> Send User ID:</blockquote>', parse_mode='HTML')
        bot.register_next_step_handler_by_chat_id(uid, do_addadm)
    elif d == 'adm_rem_adm':
        _t, _mk = _remove_admin_menu()
        bot.send_message(uid, _t, parse_mode='HTML', reply_markup=_mk)
    elif d == 'adm_list_adm':
        bot.send_message(uid, _admin_list_text(), parse_mode='HTML')
    elif d == 'adm_add_ch':
        _fj_add_start(uid)
    elif d == 'adm_rem_ch':
        bot.send_message(uid, '<blockquote> Send channel id/link:</blockquote>', parse_mode='HTML')
        bot.register_next_step_handler_by_chat_id(uid, do_remch)
    elif d == 'adm_list_ch':
        bot.send_message(uid, _fj_list_text(), parse_mode='HTML')
    elif d == 'adm_grp_mgmt':
        bot.send_message(uid, '<blockquote> Group Management</blockquote>', reply_markup=kb_group_mgmt(), parse_mode='HTML')
    elif d == 'adm_grp_ctrl':
        _send_group_control_panel(uid)
    elif d == 'adm_bot_welcome':
        bot.send_message(uid, '<blockquote> Bot Welcome Settings</blockquote>', reply_markup=kb_welcome(), parse_mode='HTML')
    elif d == 'adm_grp_welcome':
        bot.send_message(uid, '<blockquote> Group Welcome Settings</blockquote>', reply_markup=kb_group_welcome(), parse_mode='HTML')
    elif d == 'adm_api_urls':
        _send_bot_api_urls_menu(uid)
    elif d == 'adm_api_keys':
        _send_bot_api_keys_menu(uid)

def h_adback(m):
    user_state[m.from_user.id]='ADMIN_PANEL'
    bot.send_message(m.chat.id,'<blockquote><b>Admin Panel P1</b></blockquote>',reply_markup=kb_admin_p1(),parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text == ' BACK TO ADMIN P2' and is_admin(m.from_user.id))
def h_adback_p2(m):
    user_state[m.from_user.id]='ADMIN_PANEL_P2'
    bot.send_message(m.chat.id,'<blockquote><b>Admin Panel P2</b></blockquote>',reply_markup=kb_admin_p2(),parse_mode='HTML')






@bot.message_handler(func=lambda m: m.text in [' DASHBOARD', 'ᴅᴀꜱʜʙᴏᴀʀᴅ'] and is_admin(m.from_user.id))
def h_dash(m):
    tot = c.execute('SELECT COUNT(*) FROM users').fetchone()[0] or 0
    tod = c.execute("SELECT COUNT(*) FROM users WHERE DATE(join_date)=DATE('now')").fetchone()[0] or 0
    srch = c.execute('SELECT COUNT(*) FROM search_history').fetchone()[0] or 0
    grps = len(get_all_groups())
    tkns = c.execute('SELECT COUNT(*) FROM token_log').fetchone()[0] or 0
    bot.reply_to(m, f'<blockquote>📊 <b>ᴅᴀꜱʜʙᴏᴀʀᴅ</b>\n{_F}\n👥 Users: {tot} (Today: {tod})\n👥 Groups: {grps}\n🔍 Searches: {srch}\n📊 Token Logs: {tkns}\n{_F}\n⚡ @notCoder2006</blockquote>', parse_mode='HTML')
_UL_PER = 10

def _fmt_user_list_page(page=1):
    total = c.execute('SELECT COUNT(*) FROM users').fetchone()[0] or 0
    pages = max(1, (total + _UL_PER - 1) // _UL_PER)
    page = max(1, min(int(page), pages))
    offset = (page - 1) * _UL_PER
    users = c.execute('SELECT user_id,first_name,username,credits,is_premium,is_blocked FROM users ORDER BY join_date DESC LIMIT ? OFFSET ?', (_UL_PER, offset)).fetchall()

    def _te(*args, **kwargs): return ""
    _L = _te('5465270065102334742', '') * 10
    lines = []
    for u in users:
        uid_t, fname, uname, cr, prem, blocked = u
        badge = '' if prem else ''
        if blocked:
            badge = ''
        name = (fname or uname or 'User')[:14]
        lines.append(f'{badge} <code>{uid_t}</code> {name} | <b>{cr}</b>cr')
    body = '\n'.join(lines) if lines else 'No users'
    txt = f"<blockquote>{_L}\n{_te('5373012449597335010', '')} 𝗨𝗦𝗘𝗥 𝗟𝗜𝗦𝗧\n{_L}\nPage <b>{page}/{pages}</b> · Total <b>{total}</b>\n\n{body}\n\n{_L}\n⚡ @notCoder2006</blockquote>"
    mk = InlineKeyboardMarkup()
    row = []
    if page > 1:
        row.append(_IKB('Pʀᴇᴠ', style='primary', callback_data=f'ulpage_{page - 1}'))
    if page < pages:
        row.append(_IKB('Nᴇxᴛ', style='primary', callback_data=f'ulpage_{page + 1}'))
    if row:
        mk.row(*row)
    return (txt, mk)

@bot.message_handler(func=lambda m: m.text in [' USER LIST', 'ᴜꜱᴇʀ ʟɪꜱᴛ'] and is_admin(m.from_user.id))
def h_userlist(m):
    txt, mk = _fmt_user_list_page(1)
    bot.reply_to(m, txt, reply_markup=mk, parse_mode='HTML')

@bot.callback_query_handler(func=lambda c: c.data and c.data.startswith('ulpage_'))
def cb_userlist_page(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, 'Admin only')
        return
    try:
        page = int(call.data.split('_')[1])
    except:
        page = 1
    txt, mk = _fmt_user_list_page(page)
    try:
        bot.edit_message_text(txt, call.message.chat.id, call.message.message_id, reply_markup=mk, parse_mode='HTML')
    except Exception:
        bot.send_message(call.message.chat.id, txt, reply_markup=mk, parse_mode='HTML')
    try:
        bot.answer_callback_query(call.id)
    except:
        pass

@bot.message_handler(func=lambda m: m.text in [' BROADCAST', 'ʙʀᴏᴀᴅᴄᴀꜱᴛ'] and is_admin(m.from_user.id))
def h_broad(m):
    bot.register_next_step_handler(bot.reply_to(m, '<blockquote> Send message to ALL users:</blockquote>', parse_mode='HTML'), do_broadcast)

@bot.message_handler(func=lambda m: m.text in [' PREMIUM BROADCAST', 'ᴩʀᴇᴍɪᴜᴍ ʙᴄ'] and is_admin(m.from_user.id))
def h_prem_broad(m):
    user_count = c.execute('SELECT COUNT(*) FROM users WHERE is_blocked=0').fetchone()[0] or 0
    group_count = c.execute('SELECT COUNT(*) FROM groups WHERE is_blocked=0').fetchone()[0] or 0
    bot.register_next_step_handler(bot.reply_to(m, f'<blockquote>💎 <b>PREMIUM BROADCAST</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n👥 Users : <b>{user_count}</b>\n📢 Groups: <b>{group_count}</b>\n\n✅ Premium emoji FULL dikhega (hide nahi hoga)\n📋 copy_message se bheja jayega\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━\n📤 Apna message bhejo (photo/video/text sab OK):\n⚡ @notCoder2006</blockquote>', parse_mode='HTML'), do_premium_broadcast)

@bot.message_handler(func=lambda m: m.text in [' HISTORY', 'ʜɪꜱᴛᴏʀʏ'] and is_admin(m.from_user.id))
def h_hist(m):
    data = c.execute('SELECT user_id,search_type,query,search_date FROM search_history ORDER BY search_date DESC LIMIT 15').fetchall()
    txt = f'<blockquote>📜 <b>ʜɪꜱᴛᴏʀʏ</b>\n{_F}\n'
    for d in data:
        txt += f'<code>{d[0]}</code> | {d[1]} | <code>{d[2]}</code>\n'
    if not data:
        txt += 'Empty\n'
    txt += ' @notCoder2006</blockquote>'
    bot.reply_to(m, txt, parse_mode='HTML')

_BOT_APIS = [('phone', ' Phone Lookup', 'https://numbeer-info.vercel.app/?numbere={}&key=SH4DAW-D4DY'), ('userid', ' User ID', 'https://sh4dow-d4dy.vercel.app/api/search?userid={}&apikey=SH4DAW-D4DY'), ('username', 'ᴜꜱᴇʀɴᴀᴍᴇ ɪɴꜰᴏ', 'https://telegram-username-to-num.vercel.app/?key=SH4DAW-D4DY&user={}'), ('aadhar', ' Aadhar', 'https://adhar-to-info.vercel.app/?key=SH4DAW-D4DY&aadhar={}'), ('instagram', ' Instagram', 'https://insta-to-info.vercel.app/?key=SH4DAW-D4DY&username={}'), ('vehicle', ' Vehicle RC', 'https://vehicle-rc-to-num.vercel.app/?rc={}&key=SH4DAW-D4DY'), ('pan', ' PAN Card', 'https://pancard-info.deno.dev/?pan={}'), ('freefire', ' Free Fire', 'https://free-fire-info-bice.vercel.app/?uid={}&key=SH4DAW-D4DY'), ('ff_like', ' FF Like', 'https://sexty-autolikes.vercel.app/like?uid={}&region=ind'), ('bomber', ' Bomber', 'https://flix-bombar.onrender.com/bom?num={}'), ('abdulstore', ' AbdulStore', 'https://store.abdulstoreapi.workers.dev/api/v1?userid={}&key=ak_59eca148e4484ccb50e8575645c32ee1'), ('sh4dow', ' Sh4dow API', 'https://sh4dow-d4dy.vercel.app/api/search?userid={}&apikey=SH4DAW-D4DY'), ('numinfo2', ' Num Info 2', 'https://numm-info-sable.vercel.app/?key=SH4DAW-D4DY&query={}'), ('un_to_num', ' UN→Num', 'https://telegram-username-to-num.vercel.app/?key=SH4DAW-D4DY&user={}'), ('un_to_info', ' UN→Info', 'http://username-to-info-rwsw.onrender.com/info?username=@{}'), ('ff_info', ' FF Info Alt', 'https://free-fire-info-bice.vercel.app/?uid={}&key=SH4DAW-D4DY'), ('rlx_bomber', ' RLX Bomber', 'https://rlxbomber.vercel.app/api/attack?number={}&key=rlxcoder'), ('ff_like2', ' FF Like 2', 'https://verma-like-api.vercel.app/like?uid={}&region=ind')]

def _get_api_custom_url(key):
    """DB me custom URL hai to return karo, warna None"""
    try:
        r = c.execute('SELECT api_url FROM api_keys WHERE api_name=? AND is_active=1', (key,)).fetchone()
        return r[0] if r else None
    except:
        return None

def _api_source_label(key):
    custom = _get_api_custom_url(key)
    return ' Custom' if custom else ' Default'
_BOT_API_KEYS = [('key_sh4daw', ' SH4DAW (Main Key)', 'SH4DAW-D4DY'), ('key_abdulstore', ' AbdulStore Key', 'ak_59eca148e4484ccb50e8575645c32ee1'), ('key_ff_info', ' FF Info Key', 'SH4DAW-D4DY'), ('key_rlx_bomber', ' RLX Bomber Key', 'rlxcoder'), ('key_numinfo', ' NumInfo Key', 'SH4DAW-D4DY'), ('key_aadhar', ' Aadhar Key', 'SH4DAW-D4DY'), ('key_instagram', ' Instagram Key', 'SH4DAW-D4DY'), ('key_vehicle', ' Vehicle RC Key', 'SH4DAW-D4DY'), ('key_username', ' Username API Key', 'SH4DAW-D4DY')]

def _get_api_custom_key(key_name):
    """DB me custom API key hai to return karo, warna None"""
    try:
        r = c.execute('SELECT api_key FROM api_keys WHERE api_name=? AND is_active=1', (key_name,)).fetchone()
        return r[0] if r and r[0] else None
    except:
        return None

def _get_live_api_key(key_name):
    """Live API key return karo — custom DB se ya default se"""
    custom = _get_api_custom_key(key_name)
    if custom:
        return custom
    info = next((k for k in _BOT_API_KEYS if k[0] == key_name), None)
    return info[2] if info else ''

def _save_api_key(key_name, new_key, by):
    """DB me API key save karo"""
    try:
        c.execute('INSERT OR REPLACE INTO api_keys(api_name,api_url,api_key,is_active,added_by,added_date) VALUES(?,?,?,1,?,?)', (key_name, '', new_key, by, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()
        return True
    except:
        return False

def kb_bot_api_keys():
    """Inline keyboard — all API keys as buttons"""
    mk = InlineKeyboardMarkup(row_width=1)
    for key_name, label, _ in _BOT_API_KEYS:
        custom = _get_api_custom_key(key_name)
        icon = '' if custom else ''
        mk.add(_IKB(f'{icon} {label}', style='primary', callback_data=f'apikey_sel_{key_name}'))
    mk.add(_IKB(' BACK TO ADMIN', style='danger', callback_data='apikey_back'))
    return mk

def _send_bot_api_keys_menu(chat_id, msg_id=None):
    """API KEY MANAGER main screen"""
    total = len(_BOT_API_KEYS)
    custom_count = sum((1 for k, _, __ in _BOT_API_KEYS if _get_api_custom_key(k) is not None))
    default_count = total - custom_count
    txt = f'<blockquote>🔑 <b>BOT API KEY MANAGER</b>\n━━━━━━━━━━━━━━━━━━\n📊 Total Keys: {total}\n✏️ Custom Set: {custom_count}\n🗂️ Default: {default_count}\n━━━━━━━━━━━━━━━━━━\n\n🔑 Kaunsi API key change karna hai?\n<i>✏️ = Custom key already set hai</i>\n⚡ @notCoder2006</blockquote>'
    mk = kb_bot_api_keys()
    if msg_id:
        try:
            bot.edit_message_text(txt, chat_id, msg_id, reply_markup=mk, parse_mode='HTML')
            return
        except:
            pass
    bot.send_message(chat_id, txt, reply_markup=mk, parse_mode='HTML')

def kb_bot_api_urls():
    """Inline keyboard — all 21 APIs as buttons (screenshot style)"""
    mk = InlineKeyboardMarkup(row_width=1)
    for key, label, default_url in _BOT_APIS:
        source = _api_source_label(key)
        btn_label = f'{label}'
        mk.add(_IKB(btn_label, style='primary', callback_data=f'apiurl_sel_{key}'))
    mk.add(_IKB(' BACK TO ADMIN', style='danger', callback_data='apiurl_back'))
    return mk

def _send_bot_api_urls_menu(chat_id, msg_id=None):
    """BOT API URL MANAGER main screen — screenshot jaisa"""
    total = len(_BOT_APIS)
    custom_count = sum((1 for k, _, __ in _BOT_APIS if _get_api_custom_url(k) is not None))
    default_count = total - custom_count
    txt = f'<blockquote>🔗 <b>BOT API URL MANAGER</b>\n━━━━━━━━━━━━━━━━━━\n📊 Total APIs: {total}\n✏️ Custom Set: {custom_count}\n🗂️ Default: {default_count}\n━━━━━━━━━━━━━━━━━━\n\n🖊️ Kaunsi API ka URL change karna hai?\n<i>✏️ = Custom URL already set hai</i>\n⚡ @notCoder2006</blockquote>'
    mk = kb_bot_api_urls()
    if msg_id:
        try:
            bot.edit_message_text(txt, chat_id, msg_id, reply_markup=mk, parse_mode='HTML')
            return
        except:
            pass
    bot.send_message(chat_id, txt, reply_markup=mk, parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text in [' API CHANGE', ' BOT API URLS'] and is_admin(m.from_user.id))
def h_api_change(m):
    uid = m.from_user.id
    if uid != OWNER_ID:
        bot.reply_to(m, '<blockquote> Sirf owner!\n @notCoder2006</blockquote>', parse_mode='HTML')
        return
    _send_bot_api_urls_menu(m.chat.id)

@bot.message_handler(func=lambda m: m.text == ' BOT API KEYS' and is_admin(m.from_user.id))
def h_api_keys_mgmt(m):
    uid = m.from_user.id
    if uid != OWNER_ID:
        bot.reply_to(m, '<blockquote> Sirf owner!\n @notCoder2006</blockquote>', parse_mode='HTML')
        return
    _send_bot_api_keys_menu(m.chat.id)

@bot.message_handler(func=lambda m: m.chat.type == 'private' and m.from_user.id == OWNER_ID and isinstance(user_state.get(m.from_user.id), dict) and (user_state.get(m.from_user.id, {}).get('state', '') == 'API_URL_INPUT'))
def h_api_url_input(m):
    uid = m.from_user.id
    txt = m.text.strip() if m.text else ''
    st = user_state.get(uid, {})
    api_key = st.get('api_key', '')
    api_label = st.get('api_label', '')
    msg_id = st.get('prompt_msg_id')
    if txt.lower() in ['cancel', '/cancel']:
        user_state[uid] = S_NONE
        try:
            if msg_id:
                bot.delete_message(uid, msg_id)
        except:
            pass
        _send_bot_api_urls_menu(uid)
        return
    if '{}' not in txt:
        bot.reply_to(m, '<blockquote> {} placeholder zaroori hai!\nExample: <code>https://example.com/api?q={}&key=XYZ</code>\nCancel karne ke liye button dabao.</blockquote>', parse_mode='HTML')
        return
    try:
        c.execute('INSERT OR REPLACE INTO api_keys(api_name,api_url,api_key,is_active,added_by,added_date) VALUES(?,?,?,1,?,?)', (api_key, txt, '', uid, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()
    except Exception as e:
        bot.reply_to(m, f'<blockquote>❌ Error: {_safe_err(e)}</blockquote>', parse_mode='HTML')
        return
    user_state[uid] = S_NONE
    try:
        if msg_id:
            bot.delete_message(uid, msg_id)
    except:
        pass
    bot.send_message(uid, f'<blockquote>✅ 📱 <b>Phone Lookup</b> URL save ho gaya!\n\n<b>New URL:</b>\n<code>{txt}</code>\n\n⚡ @notCoder2006</blockquote>'.replace('Phone Lookup', api_label), parse_mode='HTML')
    _send_bot_api_urls_menu(uid)

@bot.message_handler(func=lambda m: m.chat.type == 'private' and m.from_user.id == OWNER_ID and isinstance(user_state.get(m.from_user.id), dict) and (user_state.get(m.from_user.id, {}).get('state', '') == 'API_KEY_INPUT'))
def h_api_key_input(m):
    """API KEY MANAGER — naya key input handler"""
    uid = m.from_user.id
    txt = m.text.strip() if m.text else ''
    st = user_state.get(uid, {})
    key_name = st.get('key_name', '')
    key_label = st.get('key_label', '')
    msg_id = st.get('prompt_msg_id')
    if txt.lower() in ['cancel', '/cancel']:
        user_state[uid] = S_NONE
        try:
            if msg_id:
                bot.delete_message(uid, msg_id)
        except:
            pass
        _send_bot_api_keys_menu(uid)
        return
    if len(txt) < 3:
        bot.reply_to(m, '<blockquote> Key bahut chhoti hai! Valid API key bhejo.\nCancel ke liye button dabao.</blockquote>', parse_mode='HTML')
        return
    if not _save_api_key(key_name, txt, uid):
        bot.reply_to(m, '<blockquote> Save error! Dobara try karo.</blockquote>', parse_mode='HTML')
        return
    user_state[uid] = S_NONE
    try:
        if msg_id:
            bot.delete_message(uid, msg_id)
    except:
        pass
    bot.send_message(uid, f'<blockquote>✅ 🔑 <b>{key_label}</b>\n\nNew Key save ho gaya!\n\n<b>Key:</b> <code>{txt}</code>\n\n⚡ @notCoder2006</blockquote>', parse_mode='HTML')
    _send_bot_api_keys_menu(uid)

def get_custom_api(feature_name):
    """DB se custom API fetch karo — agar nahi mila to None,None"""
    try:
        r = c.execute('SELECT api_url,api_key FROM api_keys WHERE api_name=? AND is_active=1', (feature_name.upper(),)).fetchone()
        if r:
            return (r[0], r[1])
    except:
        pass
    return (None, None)

def h_welcome(m):
    uid=m.from_user.id; user_state[uid]='ADMIN_WELCOME'; st=get_welcome_settings()
    img=bool(st and st[3]); vid=bool(st and st[4]); cap=(st[2] if st and st[2] else 'Welcome!')
    stk=bool(get_first_time_sticker())
    txt=f'<blockquote>👋 <b>BOT WELCOME SETTINGS</b>\n\n🖼 Image: {"✅ SET" if img else "❌ NOT SET"}\n🎥 Video: {"✅ SET" if vid else "❌ NOT SET"}\n📝 Caption: {_html.escape(str(cap)[:180])}\n🎟 First-time sticker: {"✅ SET" if stk else "❌ NOT SET"}</blockquote>'
    bot.send_message(m.chat.id,txt,reply_markup=kb_welcome(),parse_mode='HTML')

def h_grp_welcome(m):
    uid=m.from_user.id; user_state[uid]='ADMIN_GRP_WELCOME'; groups=get_all_groups()
    if not groups:
        bot.send_message(m.chat.id,'<blockquote>❌ No registered groups. Add a group first.</blockquote>',reply_markup=kb_group_welcome(),parse_mode='HTML'); return
    lines=[f'<blockquote><b>GROUP WELCOME SETTINGS</b>','',f'📋 Showing {min(len(groups),20)} of {len(groups)} groups']
    for gid,title in groups[:20]:
        img,vid,vlist,stk=get_group_welcome_media(gid)
        flags=[]
        if img: flags.append('🖼')
        if vid: flags.append('🎥')
        if vlist: flags.append('📚')
        if stk: flags.append('🎟')
        lines.append(f'\n📌 <b>{_html.escape((title or str(gid))[:30])}</b>\n<code>{gid}</code>  {" ".join(flags) if flags else "❌ No media"}')
    lines.append('</blockquote>')
    bot.send_message(m.chat.id,'\n'.join(lines),reply_markup=kb_group_welcome(),parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text == ' GROUP MANAGEMENT' and is_admin(m.from_user.id))
def h_grpmgmt(m):
    user_state[m.from_user.id] = 'ADMIN_GROUP_MANAGEMENT'
    bot.send_message(m.chat.id, '<blockquote> <b>ɢʀᴏᴜᴩ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b></blockquote>', reply_markup=kb_group_mgmt(), parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text == ' GROUP CONTROL' and is_admin(m.from_user.id))
def h_group_control(m):
    """Har group ka apna ON/OFF unlimited toggle button"""
    uid = m.from_user.id
    _send_group_control_panel(m.chat.id)

def _send_group_control_panel(chat_id,msg_id=None,page=1):
    groups=get_all_groups(); total=len(groups); pp=8
    pages=max(1,(total+pp-1)//pp)
    try: page=max(1,min(int(page),pages))
    except Exception: page=1
    if not groups:
        txt='<blockquote>🎛️ <b>GROUP CONTROL PANEL</b>\n\nNo groups registered. Use Group Management → Add Group.</blockquote>'
        mk=InlineKeyboardMarkup(row_width=1); mk.add(_IKB(' BACK TO GROUP MENU',style='danger',callback_data='grpctrl_back'))
    else:
        unlimited=sum(1 for gid,_ in groups if safe_g(get_group(gid),5)==1)
        limited=total-unlimited; start=(page-1)*pp; end=start+pp
        txt=f'<blockquote>🎛️ <b>GROUP CONTROL PANEL</b>\n\n📊 Total: <b>{total}</b>\n🟢 Unlimited: <b>{unlimited}</b> | 🔴 Limited: <b>{limited}</b>\n\n<i>Limited = normal user-credit billing. Unlimited = bypass per-user credit deduction.</i></blockquote>'
        mk=InlineKeyboardMarkup(row_width=1)
        for gid,title in groups[start:end]:
            on=safe_g(get_group(gid),5)==1
            label=('🟢 UNLIMITED' if on else '🔴 LIMITED')+' │ '+_html.escape((title or str(gid))[:28])
            mk.add(_IKB(label,style='success' if on else 'danger',callback_data=f'grpctrl_tog_{gid}_{page}'))
        nav=[]
        if page>1: nav.append(_IKB('◀ PREV',callback_data=f'grpctrl_pg_{page-1}'))
        nav.append(_IKB(f'{page}/{pages}',callback_data='noop'))
        if page<pages: nav.append(_IKB('NEXT ▶',callback_data=f'grpctrl_pg_{page+1}'))
        if len(nav)>1: mk.row(*nav)
        mk.row(_IKB(' ALL → UNLIMITED',style='success',callback_data='grpctrl_all_unl'),_IKB(' ALL → LIMITED',style='danger',callback_data='grpctrl_all_lim'))
        mk.add(_IKB(' BACK TO GROUP MENU',style='danger',callback_data='grpctrl_back'))
    if msg_id:
        try: bot.edit_message_text(txt,chat_id,msg_id,reply_markup=mk,parse_mode='HTML'); return
        except Exception: pass
    bot.send_message(chat_id,txt,reply_markup=mk,parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text == ' VIEW GROUPS' and is_admin(m.from_user.id))
def h_viewgrps(m):
    groups = get_all_groups()
    if not groups:
        bot.send_message(m.chat.id, '<blockquote> No groups.</blockquote>', parse_mode='HTML')
        return
    txt = f'<blockquote>📋 <b>ɢʀᴏᴜᴩꜱ</b>\n{_F}\n'
    for i, (gid, title) in enumerate(groups[:5], 1):
        g = get_group(gid)
        s = safe_g(g, 7)
        cr = safe_g(g, 4)
        ul = safe_g(g, 5)
        mu = safe_g(g, 8)
        txt += f"{i}. <b>{title}</b>\n<code>{gid}</code> | S:{s} | C:{('∞' if ul else cr)} {('' if mu else '')}\n\n"
    if len(groups) > 5:
        txt += f'...+{len(groups) - 5} more\n'
    txt += ' @notCoder2006</blockquote>'
    mk = kb_groups_inline()
    if mk:
        bot.send_message(m.chat.id, txt, reply_markup=mk, parse_mode='HTML')
    else:
        bot.send_message(m.chat.id, txt, parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text == ' ADD GROUP' and is_admin(m.from_user.id))
def h_addgrp(m):
    bot.register_next_step_handler(bot.reply_to(m, '<blockquote> Send group ID:</blockquote>', parse_mode='HTML'), do_addgrp)

def do_addgrp(m):
    if not is_admin(m.from_user.id): return
    try:
        gid=int((m.text or '').strip())
        if gid>=0: raise ValueError('Group ID should be negative.')
        ch=bot.get_chat(gid)
        typ=getattr(ch,'type','')
        if typ not in ('group','supergroup'): raise ValueError('This ID is not a group/supergroup.')
        title=ch.title or f'Group {gid}'
        if not add_group_to_db(gid,title,m.from_user.id): raise RuntimeError('Database save failed.')
        bot.reply_to(m,f'<blockquote>✅ <b>Group added</b>\n📌 {_html.escape(title)}\n🆔 <code>{gid}</code></blockquote>',parse_mode='HTML',reply_markup=kb_group_mgmt())
    except Exception as e:
        bot.reply_to(m,f'<blockquote>❌ {_safe_err(e)}\n\nMake sure bot is present in the group and has enough permissions.</blockquote>',parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text in [' BLOCK USER (ID)'] and is_admin(m.from_user.id))
def h_blku(m):
    bot.register_next_step_handler(bot.reply_to(m, '<blockquote>🆔 Send User ID to block:</blockquote>', parse_mode='HTML'), do_quick_ban)

@bot.message_handler(func=lambda m: m.text in [' UNBLOCK USER (ID)', 'ᴜɴʙʟᴏᴄᴋ ᴜꜱᴇʀ'] and is_admin(m.from_user.id))
def h_ublku(m):
    bot.register_next_step_handler(bot.reply_to(m, '<blockquote>🆔 Send User ID to unblock:</blockquote>', parse_mode='HTML'), do_ublku)

@bot.message_handler(func=lambda m: m.text == ' BLOCK NUMBER' and is_admin(m.from_user.id))
def h_blkn(m):
    bot.register_next_step_handler(bot.reply_to(m, '<blockquote> Send number:</blockquote>', parse_mode='HTML'), do_blkn)

@bot.message_handler(func=lambda m: m.text == ' UNBLOCK NUMBER' and is_admin(m.from_user.id))
def h_ublkn(m):
    bot.register_next_step_handler(bot.reply_to(m, '<blockquote> Send number:</blockquote>', parse_mode='HTML'), do_ublkn)

@bot.message_handler(func=lambda m: m.text == ' BLOCKED LIST' and is_admin(m.from_user.id))
def h_blklist(m):
    bl = get_blocked_identifiers()
    if not bl:
        bot.reply_to(m, '<blockquote> Empty.</blockquote>', parse_mode='HTML')
        return
    txt = f'<blockquote>📋 <b>ʙʟᴏᴄᴋᴇᴅ</b>\n{_F}\n'
    for x, t, d, r in bl[:20]:
        txt += f"🔴 {t}: <code>{x}</code> | {r or '-'}\n"
    txt += ' @notCoder2006</blockquote>'
    bot.reply_to(m, txt, parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text in [' ADD PREMIUM', 'ᴀᴅᴅ ᴩʀᴇᴍɪᴜᴍ'] and is_admin(m.from_user.id))
def h_prem(m):
    bot.register_next_step_handler(bot.reply_to(m, '<blockquote> Send: <code>uid days</code></blockquote>', parse_mode='HTML'), do_prem)

@bot.message_handler(func=lambda m: m.text in [' ADD CREDITS', 'ᴀᴅᴅ ᴄʀᴇᴅɪᴛꜱ'] and is_admin(m.from_user.id))
def h_addcr(m):
    bot.register_next_step_handler(bot.reply_to(m, '<blockquote> Send: <code>uid amount</code></blockquote>', parse_mode='HTML'), do_addcr)

@bot.message_handler(func=lambda m: m.text in [' REMOVE CREDITS', 'ʀᴇᴍᴏᴠᴇ ᴄʀᴇᴅɪᴛꜱ'] and is_admin(m.from_user.id))
def h_remcr(m):
    bot.register_next_step_handler(bot.reply_to(m, '<blockquote> Send: <code>uid amount</code></blockquote>', parse_mode='HTML'), do_remcr)

@bot.message_handler(func=lambda m: m.text in [' ADMIN MGMT', 'ᴀᴅᴍɪɴ'] and is_admin(m.from_user.id))
def h_adm(m):
    user_state[m.from_user.id] = 'ADMIN_ADMIN_MGMT'
    bot.send_message(m.chat.id, '<blockquote> <b>Admin Mgmt</b></blockquote>', reply_markup=kb_admin_mgmt(), parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text in [' ADD ADMIN', 'ᴀᴅᴅ ᴀᴅᴍɪɴ'] and is_admin(m.from_user.id))
def h_addadm(m):
    if ADMIN_MGMT_OWNER_ONLY and m.from_user.id != OWNER_ID:
        bot.reply_to(m, '<blockquote>⛔ Only the Owner can add admins.</blockquote>', parse_mode='HTML'); return
    bot.register_next_step_handler(bot.reply_to(m, '<blockquote>🆔 Send Admin User ID:</blockquote>', parse_mode='HTML'), do_addadm)

@bot.message_handler(func=lambda m: m.text in [' REMOVE ADMIN','ʀᴇᴍᴏᴠᴇ ᴀᴅᴍɪɴ'] and is_admin(m.from_user.id))
def h_remadm(m):
    if ADMIN_MGMT_OWNER_ONLY and m.from_user.id != OWNER_ID:
        bot.reply_to(m, '<blockquote>⛔ Only the Owner can remove admins.</blockquote>', parse_mode='HTML'); return
    txt = _admin_list_text().replace('✅ Every active Admin gets the full admin panel.', '🆔 <b>Send Admin User ID to remove:</b>')
    bot.register_next_step_handler(bot.reply_to(m, txt, parse_mode='HTML'), do_remadm)

@bot.message_handler(func=lambda m: m.text in [' ADMIN LIST','ᴀᴅᴍɪɴ ʟɪꜱᴛ'] and is_admin(m.from_user.id))
def h_admlist(m):
    bot.reply_to(m, _admin_list_text(), parse_mode='HTML', reply_markup=kb_admin_mgmt())

# ---------- Stability / compatibility helpers ----------

def add_group(gid, title, added_by=None):
    try:
        c.execute('INSERT OR IGNORE INTO groups(group_id,group_title,added_date,added_by,credits,unlimited,is_blocked,searches,is_muted) VALUES(?,?,?,?,0,0,0,0,0)',
                  (int(gid), str(title or f'Group {gid}'), datetime.now().strftime('%Y-%m-%d %H:%M:%S'), int(added_by) if added_by else None))
        conn.commit()
        _group_cache.pop(int(gid), None)
        return True
    except Exception as e:
        print(f'[ADD_GROUP] {e}')
        return False


def kb_menu_p2(uid=None):
    """Compatibility alias for the admin second-page keyboard."""
    try:
        return kb_admin_p2()
    except Exception:
        return InlineKeyboardMarkup()


def kb_select_user():
    """Build a real user-request keyboard when the installed pyTelegramBotAPI supports it."""
    mk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    try:
        req = KeyboardButtonRequestUser(request_id=random.randint(1000, 2147483647), user_is_bot=False)
        mk.add(KeyboardButton(' SELECT USER', request_user=req))
    except Exception:
        mk.add(KeyboardButton(' CANCEL'))
    return mk


def _api_get_json(url, params=None, timeout=20):
    try:
        r = requests.get(url, params=params, timeout=timeout)
        if r.status_code != 200:
            return None
        return r.json()
    except Exception as e:
        print(f'[API] {e}')
        return None


def _api_default_url(name):
    for key, _label, template in _BOT_APIS:
        if key == name:
            return template
    return None


def _api_with_custom(name, value, timeout=20):
    custom = _get_api_custom_url(name)
    template = custom or _api_default_url(name)
    if not template:
        return None
    key_map = {
        'aadhar': _K('key_aadhar'), 'instagram': _K('key_instagram'), 'vehicle': _K('key_vehicle'),
        'freefire': _K('key_ff_info'), 'ff_like': '', 'username': _K('key_username'),
    }
    try:
        if '{' in template:
            if 'key=' not in template and key_map.get(name):
                template = template + ('&' if '?' in template else '?') + 'key=' + str(key_map[name])
            url = template.format(value)
            return _api_get_json(url, timeout=timeout)
        params = {'key': key_map.get(name, '')} if key_map.get(name) else None
        return _api_get_json(template, params={**(params or {}), 'query': value}, timeout=timeout)
    except Exception:
        return None


def api_aadhar(an):
    raw = _luffy_get({'aadhar': str(an)}, timeout=25)
    norm = _luffy_norm_num_list(raw, str(an))
    if norm:
        return norm
    raw = _api_with_custom('aadhar', str(an), timeout=20)
    if raw is None:
        return None
    if isinstance(raw, dict) and raw.get('data') and isinstance(raw['data'], list):
        return {'success': True, 'data': raw['data'], 'total_records': len(raw['data'])}
    if isinstance(raw, list):
        return {'success': True, 'data': raw, 'total_records': len(raw)}
    if isinstance(raw, dict) and not raw.get('error'):
        return {'success': True, 'data': [raw], 'total_records': 1}
    return None


def api_instagram(username):
    raw = _api_with_custom('instagram', str(username).lstrip('@'), timeout=20)
    if raw is None:
        return None
    if isinstance(raw, dict):
        if raw.get('success') is False and raw.get('error'):
            return None
        raw['success'] = True
        return raw
    return {'success': True, 'data': raw}


def api_vehicle(rc):
    rc = str(rc).upper().strip()
    raw = _luffy_get({'rc': rc}, timeout=25)
    norm = _luffy_norm_veh(raw, rc)
    if norm:
        return norm
    raw = _api_with_custom('vehicle', rc, timeout=20)
    return _luffy_norm_veh(raw, rc) if raw else None


def api_ff(uid):
    raw = _api_with_custom('freefire', str(uid), timeout=20)
    if raw is None:
        return None
    if isinstance(raw, dict):
        if raw.get('success') is False and raw.get('error'):
            return None
        raw.setdefault('success', True)
        return raw
    return {'success': True, 'data': raw}


def api_ff_like(uid):
    raw = api_ff(uid)
    if not raw:
        return None
    data = raw.get('data') if isinstance(raw, dict) else None
    if isinstance(data, dict):
        nickname = data.get('nickname') or data.get('name') or data.get('player_name') or ''
    else:
        nickname = raw.get('nickname') or raw.get('name') or raw.get('player_name') or ''
    raw['nickname'] = nickname
    return raw

















@bot.message_handler(func=lambda m: m.text == ' CHANNEL MGMT' and is_admin(m.from_user.id))
def h_chmgmt(m):
    user_state[m.from_user.id] = 'ADMIN_CHANNEL_MGMT'
    bot.send_message(m.chat.id, '<blockquote> <b>Channel Mgmt</b></blockquote>', reply_markup=kb_channel_mgmt(), parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text == ' ADD CHANNEL' and is_admin(m.from_user.id))
def h_addch(m):
    _fj_add_start(m.from_user.id)

@bot.message_handler(func=lambda m: m.text == ' REMOVE CHANNEL' and is_admin(m.from_user.id))
def h_remch(m):
    chs = get_force_join_channels()
    if not chs:
        bot.reply_to(m, '<blockquote> Koi channel nahi hai abhi.</blockquote>', parse_mode='HTML')
        return
    txt = '<blockquote> <b>Channels (Remove ke liye ID bhejo):</b>\n\n'
    for entry in chs:
        txt += f'• <b>{entry[1]}</b>\n🆔 <code>{entry[0]}</code>\n\n'
    txt += 'Send channel ID to remove:</blockquote>'
    bot.register_next_step_handler(bot.reply_to(m, txt, parse_mode='HTML'), do_remch)

@bot.message_handler(func=lambda m: m.text == ' CHANNEL LIST' and is_admin(m.from_user.id))
def h_chlist(m):
    bot.reply_to(m, _fj_list_text(), parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text in [' GEN REDEEM CODE', 'ɢᴇɴ ʀᴇᴅᴇᴇᴍ'] and is_admin(m.from_user.id))
def h_gencode(m):
    bot.register_next_step_handler(bot.reply_to(m, '<blockquote> Send: <code>credits user_limit</code>\nExample: <code>100 5</code> → 100 credits, max 5 users\nUnlimited credits: <code>unlimited 10</code> → ∞ credits, max 10 users\n No max limit on credits amount</blockquote>', parse_mode='HTML'), do_gencode)

@bot.message_handler(func=lambda m: m.text in [' GEN PREMIUM CODE', 'ɢᴇɴ ᴩʀᴇᴍɪᴜᴍ'] and is_admin(m.from_user.id))
def h_gen_prem_code(m):
    bot.register_next_step_handler(bot.reply_to(m, f'<blockquote>🎁 <b>ɢᴇɴ ᴩʀᴇᴍɪᴜᴍ ᴄᴏᴅᴇ</b>\n{_F}\nSend: <code>days limit</code>\nExample: <code>30 1</code> → 30 din ka premium, 1 user\nExample: <code>7 5</code> → 7 din, 5 users\n💡 limit <code>0</code> = <b>UNLIMITED</b> users\n{_F}\n⚡ @notCoder2006</blockquote>', parse_mode='HTML'), do_gen_premium_code)

@bot.message_handler(func=lambda m: m.text in [' REVOKE ALL PREMIUM', 'ʀᴇᴠᴏᴋᴇ ᴩʀᴇᴍɪᴜᴍ'] and is_admin(m.from_user.id))
def h_revoke_premium(m):
    mk = InlineKeyboardMarkup()
    mk.row(_IKB(' YES, REVOKE ALL', style='danger', callback_data='confirm_revoke_premium'), _IKB(' CANCEL', style='success', callback_data='cancel_revoke_premium'))
    prem_users = c.execute('SELECT COUNT(*) FROM users WHERE is_premium=1').fetchone()[0] or 0
    prem_codes = c.execute('SELECT COUNT(*) FROM premium_codes').fetchone()[0] or 0
    bot.send_message(m.chat.id, f'<blockquote>' + _CL_TOP() + f'\n│  💀 <b>REVOKE ALL PREMIUM</b>\n' + _CL_BOT() + f'\n\n⚠️ <b>YE ACTION:</b>\n• 💎 {prem_users} users ka premium remove hoga\n• 🎟️ {prem_codes} premium codes delete honge\n• 💰 Jo credits codes se mile the, woh bhi remove honge\n• ❌ Sabhi redeemed records clear honge\n\n<b>Confirm karo?</b>\n\n{_F}\n⚡ @notCoder2006</blockquote>', reply_markup=mk, parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text == ' CLEAR HISTORY' and is_admin(m.from_user.id))
def h_clear(m):
    mk = InlineKeyboardMarkup()
    mk.row(_IKB(' YES', style='success', callback_data='confirm_clear'), _IKB(' NO', style='danger', callback_data='cancel_clear'))
    bot.send_message(m.chat.id, '<blockquote> Clear all search history?</blockquote>', reply_markup=mk, parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text == ' SET WELCOME IMAGE' and is_admin(m.from_user.id))
def h_wimg(m):
    bot.reply_to(m, '<blockquote> Send image:</blockquote>', parse_mode='HTML')
    bot.register_next_step_handler_by_chat_id(m.chat.id, do_wimg)

def do_wimg(m):
    if not is_admin(m.from_user.id): return
    if not m.photo:
        bot.reply_to(m,'<blockquote>❌ Photo bhejo.</blockquote>',parse_mode='HTML'); return
    try:
        old=get_welcome_settings(); oldv=old[3] if old else None
        c.execute('UPDATE welcome_settings SET welcome_image=? WHERE id=1',('fileid:'+m.photo[-1].file_id,)); conn.commit(); _invalidate_welcome_cache()
        if isinstance(oldv,str) and oldv and not oldv.startswith('fileid:') and os.path.exists(oldv):
            try: os.remove(oldv)
            except Exception: pass
        user_state[m.from_user.id]='ADMIN_WELCOME'
        bot.reply_to(m,'<blockquote>✅ <b>Welcome image set.</b>\nTelegram file ID saved for restart-safe storage.</blockquote>',parse_mode='HTML',reply_markup=kb_welcome())
    except Exception as e:
        bot.reply_to(m,f'<blockquote>❌ {_safe_err(e)}</blockquote>',parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text == ' SET WELCOME VIDEO' and is_admin(m.from_user.id))
def h_wvid(m):
    bot.reply_to(m, '<blockquote> Send video:</blockquote>', parse_mode='HTML')
    bot.register_next_step_handler_by_chat_id(m.chat.id, do_wvid)

def do_wvid(m):
    if not is_admin(m.from_user.id): return
    if not m.video:
        bot.reply_to(m,'<blockquote>❌ Video file bhejo.</blockquote>',parse_mode='HTML'); return
    try:
        old=get_welcome_settings(); oldv=old[4] if old else None
        c.execute('UPDATE welcome_settings SET welcome_video=? WHERE id=1',('fileid:'+m.video.file_id,)); conn.commit(); _invalidate_welcome_cache()
        if isinstance(oldv,str) and oldv and not oldv.startswith('fileid:') and os.path.exists(oldv):
            try: os.remove(oldv)
            except Exception: pass
        user_state[m.from_user.id]='ADMIN_WELCOME'
        bot.reply_to(m,'<blockquote>✅ <b>Welcome video set.</b>\nTelegram file ID saved for restart-safe storage.</blockquote>',parse_mode='HTML',reply_markup=kb_welcome())
    except Exception as e:
        bot.reply_to(m,f'<blockquote>❌ {_safe_err(e)}</blockquote>',parse_mode='HTML')

def h_wcap(m):
    if not is_admin(m.from_user.id): return
    msg=bot.reply_to(m,'<blockquote>Send welcome caption. Variables: {name} {id} {username} {credits}</blockquote>',parse_mode='HTML')
    def do(msg2):
        text=(msg2.text or '').strip()
        if not text:
            bot.reply_to(msg2,'<blockquote>❌ Caption cannot be empty.</blockquote>',parse_mode='HTML'); return
        c.execute('INSERT OR IGNORE INTO welcome_settings(id) VALUES(1)')
        c.execute('UPDATE welcome_settings SET welcome_caption=? WHERE id=1',(text[:1000],)); conn.commit(); _invalidate_welcome_cache()
        bot.reply_to(msg2,'<blockquote>✅ Welcome caption saved.</blockquote>',parse_mode='HTML',reply_markup=kb_welcome())
    bot.register_next_step_handler(msg,do)

@bot.message_handler(func=lambda m: m.text == ' SET FIRST TIME STICKER' and is_admin(m.from_user.id))
def h_stk(m):
    bot.reply_to(m, '<blockquote> Send sticker:</blockquote>', parse_mode='HTML')
    bot.register_next_step_handler_by_chat_id(m.chat.id, do_stk)

def do_stk(m):
    if not is_admin(m.from_user.id):
        return
    if m.sticker:
        c.execute('INSERT OR IGNORE INTO welcome_settings(id) VALUES(1)')
        c.execute('UPDATE welcome_settings SET first_time_sticker=? WHERE id=1', (m.sticker.file_id,))
        conn.commit()
        bot.reply_to(m, '<blockquote> <b>Sticker set!</b>\n @notCoder2006</blockquote>', parse_mode='HTML')
    else:
        bot.reply_to(m, '<blockquote> Sticker bhejo!</blockquote>', parse_mode='HTML')

def h_wreset(m):
    if not is_admin(m.from_user.id): return
    try:
        st=get_welcome_settings(); old=[st[3] if st else None,st[4] if st else None]
        c.execute("UPDATE welcome_settings SET welcome_caption='Welcome!',welcome_image=NULL,welcome_video=NULL,first_time_sticker=NULL WHERE id=1"); conn.commit(); _invalidate_welcome_cache()
        for fp in old:
            if isinstance(fp,str) and fp and not fp.startswith('fileid:') and os.path.exists(fp):
                try: os.remove(fp)
                except Exception: pass
        user_state[m.from_user.id]='ADMIN_WELCOME'
        bot.reply_to(m,'<blockquote>✅ <b>Welcome reset complete.</b> Image, video, caption and sticker cleared.</blockquote>',parse_mode='HTML',reply_markup=kb_welcome())
    except Exception as e:
        bot.reply_to(m,f'<blockquote>❌ {_safe_err(e)}</blockquote>',parse_mode='HTML')

def _gw_group_list_txt(prefix):
    groups = get_all_groups()
    if not groups:
        return (None, None)
    txt = f'<blockquote>{prefix}\n\nKis group ke liye?\n'
    for i, (gid, title) in enumerate(groups[:10], 1):
        txt += f'{i}. {title[:25]} — <code>{gid}</code>\n'
    txt += '\nGroup ID bhejo (ya 0 = all groups):\n @notCoder2006</blockquote>'
    return (txt, groups)

@bot.message_handler(func=lambda m: m.text == ' GROUP IMAGE SET' and is_admin(m.from_user.id))
def h_gwimg(m):
    txt, groups = _gw_group_list_txt(' <b>GROUP IMAGE SET</b>')
    if not txt:
        bot.reply_to(m, '<blockquote> Koi group nahi!\n @notCoder2006</blockquote>', parse_mode='HTML')
        return
    user_state[m.from_user.id] = {'state': 'GW_IMG_WAIT_GID'}
    bot.reply_to(m, txt, parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text == ' GROUP VIDEO SET' and is_admin(m.from_user.id))
def h_gwvid(m):
    txt, groups = _gw_group_list_txt(' <b>GROUP VIDEO SET</b>')
    if not txt:
        bot.reply_to(m, '<blockquote> Koi group nahi!\n @notCoder2006</blockquote>', parse_mode='HTML')
        return
    user_state[m.from_user.id] = {'state': 'GW_VID_WAIT_GID'}
    bot.reply_to(m, txt, parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text == ' GROUP VIDEO LIST' and is_admin(m.from_user.id))
def h_gwvlist(m):
    txt, groups = _gw_group_list_txt(' <b>GROUP VIDEO LIST</b>\n(1-5 videos — har member pe alag video)')
    if not txt:
        bot.reply_to(m, '<blockquote> Koi group nahi!\n @notCoder2006</blockquote>', parse_mode='HTML')
        return
    user_state[m.from_user.id] = {'state': 'GW_VLIST_WAIT_GID'}
    bot.reply_to(m, txt, parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text == ' GROUP STICKER SET' and is_admin(m.from_user.id))
def h_gwstk(m):
    txt, groups = _gw_group_list_txt(' <b>GROUP STICKER SET</b>\n Sticker sirf GROUP welcome mein — BOT DM mein nahi')
    if not txt:
        bot.reply_to(m, '<blockquote> Koi group nahi!\n @notCoder2006</blockquote>', parse_mode='HTML')
        return
    user_state[m.from_user.id] = {'state': 'GW_STK_WAIT_GID'}
    bot.reply_to(m, txt, parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text == ' GROUP WELCOME TEXT' and is_admin(m.from_user.id))
def h_gwtxt(m):
    txt, groups = _gw_group_list_txt(' <b>GROUP WELCOME TEXT</b>\nVariables: {name} {id} {username} {group}')
    if not txt:
        bot.reply_to(m, '<blockquote> Koi group nahi!\n @notCoder2006</blockquote>', parse_mode='HTML')
        return
    user_state[m.from_user.id] = {'state': 'GW_TXT_WAIT_GID'}
    bot.reply_to(m, txt, parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text == ' GROUP WELCOME RESET' and is_admin(m.from_user.id))
def h_gwreset(m):
    txt, groups = _gw_group_list_txt(' <b>GROUP WELCOME RESET</b>\n(0 = ALL groups reset)')
    if not txt:
        bot.reply_to(m, '<blockquote> Koi group nahi!\n @notCoder2006</blockquote>', parse_mode='HTML')
        return
    user_state[m.from_user.id] = {'state': 'GW_RESET_WAIT_GID'}
    bot.reply_to(m, txt, parse_mode='HTML')

def h_gw_state(m):
    uid=m.from_user.id; st=user_state.get(uid,{}) ; state=st.get('state','') if isinstance(st,dict) else ''
    valid=[gid for gid,_ in get_all_groups()]; valid_set=set(valid)
    if state.endswith('_WAIT_GID'):
        try:
            val=int((m.text or '').strip())
        except Exception:
            bot.reply_to(m,'<blockquote>❌ Valid group ID bhejo.</blockquote>',parse_mode='HTML'); return
        gids=valid if val==0 else ([val] if val in valid_set else [])
        if not gids:
            bot.reply_to(m,'<blockquote>❌ Ye group registered nahi hai. Pehle Group Management → Add Group use karo.</blockquote>',parse_mode='HTML'); return
        if state=='GW_RESET_WAIT_GID':
            now=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            for gid in gids:
                c.execute("UPDATE group_welcome_settings SET welcome_on=1,group_rules='',welcome_image=NULL,welcome_video=NULL,video_list=NULL,group_sticker=NULL,welcome_text=NULL,bye_on=1,updated_date=? WHERE group_id=?",(now,gid))
            conn.commit(); user_state[uid]={'state':'ADMIN_GRP_WELCOME'}
            bot.reply_to(m,f'<blockquote>✅ <b>{len(gids)} group(s) reset.</b> Welcome settings, media, text and rules cleared.</blockquote>',parse_mode='HTML',reply_markup=kb_group_welcome()); return
        next_state=state.replace('_WAIT_GID','_WAIT_MEDIA'); user_state[uid]={'state':next_state,'gids':gids,'vlist':[]}
        prompts={'GW_IMG_WAIT_MEDIA':'Send the group welcome image.','GW_VID_WAIT_MEDIA':'Send the group welcome video.','GW_VLIST_WAIT_MEDIA':'Send 1-5 Telegram videos. Send DONE when finished.','GW_STK_WAIT_MEDIA':'Send the welcome sticker.','GW_TXT_WAIT_MEDIA':'Send welcome text. Variables: {name} {id} {username} {group}'}
        bot.reply_to(m,f'<blockquote>{prompts.get(next_state,"Send media")}</blockquote>',parse_mode='HTML'); return
    gids=st.get('gids',[]) if isinstance(st,dict) else []
    if not gids:
        user_state[uid]='none'; return
    if state=='GW_IMG_WAIT_MEDIA':
        if not m.photo:
            bot.reply_to(m,'<blockquote>❌ Photo bhejo.</blockquote>',parse_mode='HTML'); return
        for gid in gids: set_group_welcome_image(gid,'fileid:'+m.photo[-1].file_id)
        user_state[uid]={'state':'ADMIN_GRP_WELCOME'}; bot.reply_to(m,f'<blockquote>✅ Group image set for {len(gids)} group(s).</blockquote>',parse_mode='HTML',reply_markup=kb_group_welcome()); return
    if state=='GW_VID_WAIT_MEDIA':
        if not m.video:
            bot.reply_to(m,'<blockquote>❌ Video bhejo.</blockquote>',parse_mode='HTML'); return
        for gid in gids: set_group_welcome_video(gid,'fileid:'+m.video.file_id)
        user_state[uid]={'state':'ADMIN_GRP_WELCOME'}; bot.reply_to(m,f'<blockquote>✅ Group video set for {len(gids)} group(s).</blockquote>',parse_mode='HTML',reply_markup=kb_group_welcome()); return
    if state=='GW_VLIST_WAIT_MEDIA':
        vlist=list(st.get('vlist',[]))
        if m.text and m.text.strip().upper()=='DONE':
            if not vlist:
                bot.reply_to(m,'<blockquote>❌ Add at least one video first.</blockquote>',parse_mode='HTML'); return
            for gid in gids: set_group_welcome_video_list(gid,json.dumps(vlist[:5]))
            user_state[uid]={'state':'ADMIN_GRP_WELCOME'}; bot.reply_to(m,f'<blockquote>✅ {len(vlist[:5])} video(s) saved for {len(gids)} group(s).</blockquote>',parse_mode='HTML',reply_markup=kb_group_welcome()); return
        fid=None
        if m.video: fid=m.video.file_id
        elif getattr(m,'document',None) and getattr(m.document,'mime_type','') and m.document.mime_type.startswith('video/'): fid=m.document.file_id
        if not fid:
            bot.reply_to(m,'<blockquote>❌ Send a video file or DONE.</blockquote>',parse_mode='HTML'); return
        if len(vlist)>=5:
            bot.reply_to(m,'<blockquote>Maximum 5 videos reached. Send DONE.</blockquote>',parse_mode='HTML'); return
        vlist.append(fid); user_state[uid]={'state':state,'gids':gids,'vlist':vlist}
        bot.reply_to(m,f'<blockquote>✅ Video {len(vlist)}/5 added. Send another or DONE.</blockquote>',parse_mode='HTML'); return
    if state=='GW_STK_WAIT_MEDIA':
        if not m.sticker:
            bot.reply_to(m,'<blockquote>❌ Sticker bhejo.</blockquote>',parse_mode='HTML'); return
        for gid in gids: set_group_welcome_sticker(gid,m.sticker.file_id)
        user_state[uid]={'state':'ADMIN_GRP_WELCOME'}; bot.reply_to(m,f'<blockquote>✅ Sticker set for {len(gids)} group(s).</blockquote>',parse_mode='HTML',reply_markup=kb_group_welcome()); return
    if state=='GW_TXT_WAIT_MEDIA':
        text=(m.text or '').strip()
        if not text:
            bot.reply_to(m,'<blockquote>❌ Text bhejo.</blockquote>',parse_mode='HTML'); return
        now=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        for gid in gids:
            c.execute("INSERT OR IGNORE INTO group_welcome_settings(group_id,welcome_on,group_rules,updated_date) VALUES(?,1,'',?)",(gid,now))
            c.execute('UPDATE group_welcome_settings SET welcome_text=?,updated_date=? WHERE group_id=?',(text[:3000],now,gid))
        conn.commit(); user_state[uid]={'state':'ADMIN_GRP_WELCOME'}; bot.reply_to(m,f'<blockquote>✅ Welcome text saved for {len(gids)} group(s).</blockquote>',parse_mode='HTML',reply_markup=kb_group_welcome()); return

@bot.message_handler(func=lambda m: m.text in [' TOGGLE FEATURES', 'ᴛᴏɢɢʟᴇ ꜰᴇᴀᴛᴜʀᴇꜱ', 'TOGGLE FEATURES'] and is_admin(m.from_user.id))
def h_toggle_features(m):
    uid = m.from_user.id
    user_state[uid] = 'ADMIN_FEATURE_TOGGLE'
    bot.send_message(m.chat.id, f'<blockquote>━━━━━━━━━━━━━━━━━━━━━━━━━━━\n⚙️ <b>ꜰᴇᴀᴛᴜʀᴇ ᴛᴏɢɢʟᴇ</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n✅ = ON   |   ❌ = OFF\nKisi bhi button ko tap karo toggle karne ke liye:\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━\n⚡ @notCoder2006</blockquote>', reply_markup=kb_features(), parse_mode='HTML')

def cb_ftog(call):
    uid=call.from_user.id
    fn=(call.data or '')[5:]
    if fn=='back':
        try: bot.delete_message(call.message.chat.id,call.message.message_id)
        except Exception: pass
        bot.send_message(uid,'<blockquote><b>Admin Panel P2</b></blockquote>',reply_markup=kb_admin_p2(),parse_mode='HTML')
        bot.answer_callback_query(call.id,'Back to Admin')
        return
    if fn!='number':
        bot.answer_callback_query(call.id,'Invalid feature!')
        return
    state=toggle_feature('number',uid)
    bot.answer_callback_query(call.id,f"NUMBER INFO → {'ON' if state else 'OFF'}")
    try: bot.edit_message_reply_markup(call.message.chat.id,call.message.message_id,reply_markup=kb_features())
    except Exception: pass


def do_broadcast(m):
    if not is_admin(m.from_user.id):
        return
    users = c.execute('SELECT user_id FROM users WHERE is_blocked=0').fetchall()
    groups = c.execute('SELECT group_id FROM groups WHERE is_blocked=0').fetchall()
    tot = len(users) + len(groups)
    sent = 0
    fail = 0
    sm = bot.reply_to(m, f'<blockquote>📢 Broadcasting to {len(users)} users + {len(groups)} groups...</blockquote>', parse_mode='HTML')

    def _send_one(chat_id):
        """copy_message — premium tg-emoji ke saath exact copy, hide nahi hoga"""
        try:
            bot.copy_message(chat_id, m.chat.id, m.message_id)
            return True
        except:
            try:
                if m.content_type == 'text':
                    bot.send_message(chat_id, m.text, parse_mode='HTML')
                elif m.content_type == 'photo':
                    bot.send_photo(chat_id, m.photo[-1].file_id, caption=m.caption or '', parse_mode='HTML')
                elif m.content_type == 'video':
                    bot.send_video(chat_id, m.video.file_id, caption=m.caption or '', parse_mode='HTML')
                elif m.content_type == 'sticker':
                    bot.send_sticker(chat_id, m.sticker.file_id)
                elif m.content_type == 'document':
                    bot.send_document(chat_id, m.document.file_id, caption=m.caption or '', parse_mode='HTML')
                elif m.content_type == 'animation':
                    bot.send_animation(chat_id, m.animation.file_id, caption=m.caption or '', parse_mode='HTML')
                elif m.content_type == 'voice':
                    bot.send_voice(chat_id, m.voice.file_id)
                elif m.content_type == 'audio':
                    bot.send_audio(chat_id, m.audio.file_id, caption=m.caption or '', parse_mode='HTML')
                return True
            except:
                return False
    for uid, in users:
        if _send_one(uid):
            sent += 1
        else:
            fail += 1
        time.sleep(0.04)
    for gid, in groups:
        if _send_one(gid):
            sent += 1
        else:
            fail += 1
        time.sleep(0.05)
    try:
        bot.edit_message_text(f'<blockquote>✅ <b>Broadcast Done!</b>\n👥 Users: <b>{len(users)}</b> | 📢 Groups: <b>{len(groups)}</b>\n✅ Sent: <b>{sent}</b> | ❌ Failed: <b>{fail}</b>\n⚡ @notCoder2006</blockquote>', sm.chat.id, sm.message_id, parse_mode='HTML')
    except:
        pass

def do_premium_broadcast(m):
    '\n     PREMIUM BROADCAST — Sab users + groups ko copy_message se bhejo.\n    copy_message → tg-emoji / premium emoji FULLY visible, hide nahi hoga.\n    '
    if not is_admin(m.from_user.id):
        return
    users = c.execute('SELECT user_id FROM users WHERE is_blocked=0').fetchall()
    groups = c.execute('SELECT group_id FROM groups WHERE is_blocked=0').fetchall()
    total = len(users) + len(groups)
    sent = 0
    fail = 0
    sm = bot.reply_to(m, f'<blockquote>💎 <b>PREMIUM BROADCAST</b>\n👥 Users: <b>{len(users)}</b> | 📢 Groups: <b>{len(groups)}</b>\n\n⏳ Sending with full premium emoji...</blockquote>', parse_mode='HTML')

    def _copy_one(chat_id):
        """copy_message — premium tg-emoji ke saath exact copy, bilkul hide nahi hoga"""
        try:
            bot.copy_message(chat_id, m.chat.id, m.message_id)
            return True
        except:
            try:
                if m.content_type == 'text':
                    bot.send_message(chat_id, m.text, parse_mode='HTML')
                elif m.content_type == 'photo':
                    bot.send_photo(chat_id, m.photo[-1].file_id, caption=m.caption or '', parse_mode='HTML')
                elif m.content_type == 'video':
                    bot.send_video(chat_id, m.video.file_id, caption=m.caption or '', parse_mode='HTML')
                elif m.content_type == 'sticker':
                    bot.send_sticker(chat_id, m.sticker.file_id)
                elif m.content_type == 'document':
                    bot.send_document(chat_id, m.document.file_id, caption=m.caption or '', parse_mode='HTML')
                elif m.content_type == 'animation':
                    bot.send_animation(chat_id, m.animation.file_id, caption=m.caption or '', parse_mode='HTML')
                elif m.content_type == 'voice':
                    bot.send_voice(chat_id, m.voice.file_id)
                elif m.content_type == 'audio':
                    bot.send_audio(chat_id, m.audio.file_id, caption=m.caption or '', parse_mode='HTML')
                return True
            except:
                return False
    for recv_uid, in users:
        if _copy_one(recv_uid):
            sent += 1
        else:
            fail += 1
        time.sleep(0.04)
    for gid, in groups:
        if _copy_one(gid):
            sent += 1
        else:
            fail += 1
        time.sleep(0.05)
    try:
        bot.edit_message_text(f'<blockquote>✅ <b>💎 Premium Broadcast Done!</b>\n\n👥 Users: <b>{len(users)}</b> | 📢 Groups: <b>{len(groups)}</b>\n✅ Sent: <b>{sent}</b> | ❌ Failed: <b>{fail}</b>\n\n💎 Premium emoji — fully visible!\n⚡ @notCoder2006</blockquote>', sm.chat.id, sm.message_id, parse_mode='HTML')
    except:
        pass

def do_blku(m):
    do_quick_ban(m)

def do_ublku(m):
    if not is_admin(m.from_user.id):
        return
    t = _parse_uid(m.text)
    if t is None:
        bot.reply_to(m, '<blockquote>❌ Invalid User ID! Numeric Telegram ID bhejo.</blockquote>', parse_mode='HTML'); return
    try:
        if _unban_user(t):
            bot.reply_to(m, f'<blockquote>✅ User <code>{t}</code> unblocked!</blockquote>', parse_mode='HTML')
        else:
            bot.reply_to(m, f'<blockquote>⚠️ User <code>{t}</code> is not blocked.</blockquote>', parse_mode='HTML')
    except Exception as e:
        bot.reply_to(m, f'<blockquote>❌ Database error: {_safe_err(e)}</blockquote>', parse_mode='HTML')

def do_blkn(m):
    if not is_admin(m.from_user.id):
        return
    n = re.sub('\\D', '', m.text.strip())
    if len(n) != 10:
        bot.reply_to(m, '<blockquote> Invalid!</blockquote>', parse_mode='HTML')
        return
    block_identifier(n, 'number', m.from_user.id, 'Blocked')
    bot.reply_to(m, f'<blockquote>✅ Number blocked!</blockquote>', parse_mode='HTML')

def do_ublkn(m):
    if not is_admin(m.from_user.id):
        return
    if unblock_identifier(m.text.strip()):
        bot.reply_to(m, '<blockquote> Unblocked!</blockquote>', parse_mode='HTML')
    else:
        bot.reply_to(m, '<blockquote> Not found!</blockquote>', parse_mode='HTML')

def do_prem(m):
    if not is_admin(m.from_user.id):
        return
    try:
        p = m.text.split()
        uid_t, days = (int(p[0]), int(p[1]))
        until = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')
        update_user(uid_t, is_premium=1, premium_until=until)
        bot.reply_to(m, f'<blockquote>✅ Premium {days} days to <code>{uid_t}</code>!</blockquote>', parse_mode='HTML')
    except:
        bot.reply_to(m, '<blockquote> Format: uid days</blockquote>', parse_mode='HTML')

def do_addcr(m):
    if not is_admin(m.from_user.id):
        return
    try:
        p = m.text.split()
        uid_t, cr = (int(p[0]), int(p[1]))
        c.execute('UPDATE users SET credits=credits+? WHERE user_id=?', (cr, uid_t))
        conn.commit()
        bot.reply_to(m, f'<blockquote>✅ +{cr} credits to <code>{uid_t}</code>!</blockquote>', parse_mode='HTML')
    except:
        bot.reply_to(m, '<blockquote> Format: uid amount</blockquote>', parse_mode='HTML')

def do_remcr(m):
    if not is_admin(m.from_user.id):
        return
    try:
        p = m.text.split()
        uid_t, amt = (int(p[0]), int(p[1]))
        user = get_user(uid_t)
        if not user:
            bot.reply_to(m, '<blockquote> User not found!</blockquote>', parse_mode='HTML')
            return
        nc = max(0, user[5] - amt)
        c.execute('UPDATE users SET credits=? WHERE user_id=?', (nc, uid_t))
        conn.commit()
        bot.reply_to(m, f'<blockquote>✅ -{amt} credits. New: {nc}</blockquote>', parse_mode='HTML')
    except:
        bot.reply_to(m, '<blockquote> Format: uid amount</blockquote>', parse_mode='HTML')

def do_addadm(m):
    actor = m.from_user.id
    if not is_admin(actor): return
    if ADMIN_MGMT_OWNER_ONLY and actor != OWNER_ID:
        bot.reply_to(m, '<blockquote>⛔ Only the Owner can add admins.</blockquote>', parse_mode='HTML'); return
    target = _parse_uid(m.text)
    if target is None:
        bot.reply_to(m, '<blockquote>❌ Invalid User ID! Numeric Telegram ID bhejo.</blockquote>', parse_mode='HTML'); return
    try:
        if target == OWNER_ID or is_admin(target):
            bot.reply_to(m, '<blockquote>⚠️ This user is already an Admin.</blockquote>', parse_mode='HTML', reply_markup=kb_admin_mgmt()); return
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        c.execute('INSERT OR IGNORE INTO admins(user_id,added_by,added_date,is_active) VALUES(?,?,?,1)', (target, actor, now))
        c.execute('UPDATE admins SET added_by=?,added_date=?,is_active=1 WHERE user_id=?', (actor, now, target))
        conn.commit(); _admin_cache[target] = True
        bot.reply_to(m, f'<blockquote>✅ <b>Admin added</b>\n🆔 <code>{target}</code>\n🔐 Full Admin Panel access is now active.</blockquote>', parse_mode='HTML', reply_markup=kb_admin_mgmt())
    except Exception as e:
        bot.reply_to(m, f'<blockquote>❌ Database error: {_safe_err(e)}</blockquote>', parse_mode='HTML')

def do_remadm(m):
    actor = m.from_user.id
    if not is_admin(actor): return
    if ADMIN_MGMT_OWNER_ONLY and actor != OWNER_ID:
        bot.reply_to(m, '<blockquote>⛔ Only the Owner can remove admins.</blockquote>', parse_mode='HTML'); return
    target = _parse_uid(m.text)
    if target is None:
        bot.reply_to(m, '<blockquote>❌ Invalid User ID!</blockquote>', parse_mode='HTML'); return
    ok, msg = _remove_admin(target)
    bot.reply_to(m, f'<blockquote>{msg}</blockquote>', parse_mode='HTML', reply_markup=kb_admin_mgmt())

def do_addch(m):
    if not is_admin(m.from_user.id): return
    try:
        raw=(m.text or '').strip()
        if raw.startswith('@'):
            target=raw; url='https://t.me/'+raw[1:]
        elif re.match(r'^https?://t\.me/[^/]+/?$',raw,re.I):
            tail=re.split(r't\.me/',raw,flags=re.I,maxsplit=1)[1].strip('/')
            if tail.startswith('+') or tail.lower().startswith('joinchat/'): raise ValueError('Private invite verification is not supported here. Use a public @username or numeric channel ID.')
            target='@'+tail; url=raw.rstrip('/')
        elif re.match(r'^-100\d{5,}$',raw):
            target=raw; url=''
        else:
            raise ValueError('Format: @channelusername, https://t.me/channelusername or -100...')
        ch=bot.get_chat(target)
        if getattr(ch,'type','')!='channel': raise ValueError('Given chat is not a channel.')
        cid=str(ch.id); title=ch.title or target.lstrip('@'); un=getattr(ch,'username',None)
        if not url and un:
            url='https://t.me/'+un
        if not url:
            raise ValueError('Channel needs a public @username or public https://t.me/... join link.')
        try:
            me=bot.get_me(); bot.get_chat_member(ch.id,me.id)
        except Exception:
            raise ValueError('Bot must be an administrator in the channel.')
        now=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        c.execute('INSERT OR REPLACE INTO force_join_channels(chat_id,chat_title,chat_url,added_by,added_date,is_active) VALUES(?,?,?,?,?,1)',(cid,title,url,m.from_user.id,now)); conn.commit()
        bot.reply_to(m,f'<blockquote>✅ <b>Channel added</b>\n📢 {_html.escape(title)}\n🆔 <code>{cid}</code>\n🔗 {url or "No public username"}</blockquote>',parse_mode='HTML',reply_markup=kb_channel_mgmt())
    except Exception as e:
        bot.reply_to(m,f'<blockquote>❌ Channel add failed: {_safe_err(e)}</blockquote>',parse_mode='HTML')

def do_remch(m):
    if not is_admin(m.from_user.id): return
    key=(m.text or '').strip(); norm=_fj_normalize(key)
    if not key:
        bot.reply_to(m,'<blockquote>Channel ID/link/username bhejo.</blockquote>',parse_mode='HTML'); return
    if norm in {_fj_normalize(x[0]) for x in FORCE_JOIN_DEFAULT_CHANNELS}:
        bot.reply_to(m,'<blockquote>⚠️ Default force-join channel cannot be removed here.</blockquote>',parse_mode='HTML',reply_markup=kb_channel_mgmt()); return
    rows=c.execute('SELECT id,chat_id,chat_title,chat_url FROM force_join_channels WHERE is_active=1').fetchall(); rid=None
    for row in rows:
        if norm in {_fj_normalize(row[1]),_fj_normalize(row[2]),_fj_normalize(row[3])}: rid=row[0]; break
    if rid is None:
        bot.reply_to(m,'<blockquote>❌ Active channel not found.</blockquote>',parse_mode='HTML',reply_markup=kb_channel_mgmt()); return
    c.execute('UPDATE force_join_channels SET is_active=0 WHERE id=?',(rid,)); conn.commit()
    bot.reply_to(m,'<blockquote>✅ Channel removed.</blockquote>',parse_mode='HTML',reply_markup=kb_channel_mgmt())

def do_gencode(m):
    if not is_admin(m.from_user.id):
        return
    try:
        p = m.text.strip().split()
        if not p:
            raise ValueError('empty')
        raw0 = p[0].lower()
        if raw0 in ('unlimited', 'inf', '∞', '-1'):
            cr = -1
        else:
            cr = int(p[0])
        lim = int(p[1]) if len(p) > 1 else 1
        code = generate_code()
        c.execute('INSERT INTO redeem_codes(code,credits,redeem_limit,created_by,created_date) VALUES(?,?,?,?,?)', (code, cr, lim, m.from_user.id, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()
        _rem_txt = ''
        _cr_show = 'UNLIMITED' if cr == -1 else str(cr)
        _lim_show = 'Unlimited users' if lim == 0 else str(lim)
        bot.reply_to(m, f'<blockquote>✅ <b>Code Generated!</b>\n🎫 Code: <code>{code}</code>\n💰 Credits: <b>{_cr_show}</b>\n🔢 User limit: <b>{_lim_show}</b>{_rem_txt}\n⚡ @notCoder2006</blockquote>', parse_mode='HTML')
    except Exception as e:
        bot.reply_to(m, f'<blockquote>❌ {_safe_err(e)}</blockquote>', parse_mode='HTML')

def do_gen_premium_code(m):
    if not is_admin(m.from_user.id):
        return
    try:
        p = m.text.strip().split()
        days = int(p[0])
        lim = int(p[1]) if len(p) > 1 else 1
        code = generate_premium_code()
        c.execute('INSERT INTO premium_codes(code,days,redeem_limit,created_by,created_date) VALUES(?,?,?,?,?)', (code, days, lim, m.from_user.id, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()
        bot.reply_to(m, f"<blockquote>💎 <b>ᴩʀᴇᴍɪᴜᴍ ᴄᴏᴅᴇ ɢᴇɴᴇʀᴀᴛᴇᴅ!</b>\n{_F}\n🔑 Code: <code>{code}</code>\n📅 Days: <b>{days}</b>\n🔢 Limit: <b>{lim}</b> user{('s' if lim > 1 else '')}\n{_F}\n📤 User is ko /premium se redeem kare\n⚡ @notCoder2006</blockquote>", parse_mode='HTML')
    except Exception as e:
        bot.reply_to(m, f'<blockquote>❌ Format: days limit\nExample: 30 1\n{_safe_err(e)}</blockquote>', parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text in [' LIVE STATS', 'ʟɪᴠᴇ ꜱᴛᴀᴛꜱ'] and is_admin(m.from_user.id))
def h_live_stats(m):
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        total_users = c.execute('SELECT COUNT(*) FROM users').fetchone()[0] or 0
        searches_today = c.execute('SELECT COUNT(*) FROM search_history WHERE search_date LIKE ?', (today + '%',)).fetchone()[0] or 0
        joins_today = c.execute('SELECT COUNT(*) FROM users WHERE join_date LIKE ?', (today + '%',)).fetchone()[0] or 0
        refs_today = c.execute('SELECT COUNT(*) FROM referrals WHERE date LIKE ?', (today + '%',)).fetchone()[0] or 0
        top = c.execute('SELECT user_id, COUNT(*) as cnt FROM search_history WHERE search_date LIKE ? GROUP BY user_id ORDER BY cnt DESC LIMIT 5', (today + '%',)).fetchall()
        top_txt = ''
        for i, (uid_t, cnt) in enumerate(top, 1):
            u = get_user(uid_t)
            nm = (u[2] if u else str(uid_t)) or str(uid_t)
            top_txt += f'{i}. <code>{uid_t}</code> {nm} — <b>{cnt}</b>\n'
        if not top_txt:
            top_txt = 'No searches today\n'
        prem_today = c.execute('SELECT COUNT(*) FROM redeemed_premium WHERE redeem_date LIKE ?', (today + '%',)).fetchone()[0] or 0
        bot.reply_to(m, f"<blockquote>📊 <b>LIVE STATS</b>\n━━━━━━━━━━━━━━━━━━\n👥 Total users: <b>{total_users}</b>\n🆕 Joins today: <b>{joins_today}</b>\n🔍 Searches today: <b>{searches_today}</b>\n🔗 Refers today: <b>{refs_today}</b>\n💎 Premium redeems today: <b>{prem_today}</b>\n🎁 Referral bonus: <b>+{get_referral_bonus()}</b>\n🛠 Maintenance: <b>{('ON' if is_maintenance() else 'OFF')}</b>\n━━━━━━━━━━━━━━━━━━\n🏆 <b>Top searchers today</b>\n{top_txt}━━━━━━━━━━━━━━━━━━\n⚡ @notCoder2006</blockquote>", parse_mode='HTML')
    except Exception as e:
        bot.reply_to(m, f'<blockquote>❌ {_safe_err(e)}</blockquote>', parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text in [' API STATUS', 'ᴀᴩɪ ꜱᴛᴀᴛᴜꜱ'] and is_admin(m.from_user.id))
def h_api_status(m):
    sm = bot.reply_to(m, '<blockquote> Checking APIs...</blockquote>', parse_mode='HTML')
    checks = []

    def _ping(name, url, timeout=8):
        try:
            r = requests.get(url, timeout=timeout)
            ok = r.status_code == 200
            checks.append(f"{('' if ok else '')} <b>{name}</b> — {r.status_code} ({timeout}s)")
        except Exception as e:
            checks.append(f'❌ <b>{name}</b> — fail')
    _ping('Number Info', 'https://apihub-livid.vercel.app/api/number-info?key=hacker_62912388cf9ac45e04&mobile=9876543210')
    _ping('TG Ultra', 'https://shivam-ultra-api.vercel.app/tg?key=Y&id=1')
    _ping('TG user-to-num', 'https://user-to-num-info-zcpe.onrender.com/userid=1')
    try:
        bot.edit_message_text(f'<blockquote>🔌 <b>API STATUS</b>\n━━━━━━━━━━━━━━━━━━\n' + '\n'.join(checks) + '\n━━━━━━━━━━━━━━━━━━\n @notCoder2006</blockquote>', m.chat.id, sm.message_id, parse_mode='HTML')
    except:
        bot.send_message(m.chat.id, '\n'.join(checks), parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text in [' MAINTENANCE', 'ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ', 'ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ ᴍᴏᴅᴇ'] and is_admin(m.from_user.id))
def h_maintenance(m):
    bot.reply_to(m, _maint_menu_text(), reply_markup=_maint_menu_kb(), parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text in ['ᴍᴀɪɴᴛ ᴍꜱɢ', 'MAINT MSG'] and is_admin(m.from_user.id))
def h_maint_msg(m):
    cur = _get_setting('maintenance_msg', ' Bot under maintenance\nThodi der baad try karo.')
    bot.register_next_step_handler(bot.reply_to(m, f'<blockquote>✏️ <b>Maintenance Message Editor</b>\n\nCurrent:\n<code>{cur}</code>\n\nSend new message text (HTML ok):</blockquote>', parse_mode='HTML'), do_set_maint_msg)

def do_set_maint_msg(m):
    if not is_admin(m.from_user.id):
        return
    msg = (m.text or '').strip()
    if not msg or len(msg) > 500:
        bot.reply_to(m, '<blockquote> Empty or too long (max 500)</blockquote>', parse_mode='HTML')
        return
    _set_setting('maintenance_msg', msg)
    bot.reply_to(m, f'<blockquote>✅ Saved!\n\nPreview:\n{msg}</blockquote>', parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text in [' REFERRAL BONUS', 'ʀᴇꜰᴇʀʀᴀʟ ʙᴏɴᴜꜱ', 'ʀᴇꜰᴇʀʀᴀʟ ꜱᴇᴛᴛɪɴɢ'] and is_admin(m.from_user.id))
def h_ref_bonus(m):
    bot.register_next_step_handler(bot.reply_to(m, f'<blockquote>🎁 <b>ʀᴇꜰᴇʀʀᴀʟ ꜱᴇᴛᴛɪɴɢ</b>\n\nPER REFERRAL = <b>{get_referral_bonus()}</b> COINS\n\nSend new coins value (e.g. <code>5</code>):</blockquote>', parse_mode='HTML'), do_set_ref_bonus)

def do_set_ref_bonus(m):
    if not is_admin(m.from_user.id):
        return
    raw = (m.text or '').strip()
    if not re.fullmatch(r'\d{1,4}', raw) or not (0 <= int(raw) <= 1000):
        bot.reply_to(m, '<blockquote>❌ Invalid value! Sirf number bhejo (0 se 1000 tak).</blockquote>', parse_mode='HTML'); return
    if not _set_setting('referral_bonus', str(int(raw))):
        bot.reply_to(m, '<blockquote>❌ Database error: value save nahi hui.</blockquote>', parse_mode='HTML'); return
    bot.reply_to(m, f'<blockquote>✅ <b>Saved!</b>\nPER REFERRAL = <b>{int(raw)}</b> COINS</blockquote>', parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text in [' QUICK BAN', 'ǫᴜɪᴄᴋ ʙᴀɴ'] and is_admin(m.from_user.id))
def h_quick_ban(m):
    bot.register_next_step_handler(bot.reply_to(m, '<blockquote>🆔 Send User ID to block:</blockquote>', parse_mode='HTML'), do_quick_ban)

def do_quick_ban(m):
    if not is_admin(m.from_user.id):
        return
    t = _parse_uid(m.text)
    if t is None:
        bot.reply_to(m, '<blockquote>❌ Invalid User ID! Numeric Telegram ID bhejo.</blockquote>', parse_mode='HTML'); return
    if t == OWNER_ID or is_admin(t):
        bot.reply_to(m, "<blockquote>⛔ Can't block this user!</blockquote>", parse_mode='HTML'); return
    try:
        if is_user_banned(t):
            bot.reply_to(m, f'<blockquote>⚠️ User <code>{t}</code> is already blocked.</blockquote>', parse_mode='HTML'); return
        _ban_user(t, m.from_user.id)
        bot.reply_to(m, f'<blockquote>✅ User <code>{t}</code> blocked!</blockquote>', parse_mode='HTML')
    except Exception as e:
        bot.reply_to(m, f'<blockquote>❌ Database error: {_safe_err(e)}</blockquote>', parse_mode='HTML')

# ======================= ADMIN / BAN / MAINTENANCE / TARGET HELPERS =======================
ADMIN_MGMT_OWNER_ONLY = False   # True = sirf OWNER admin add/remove kar sakta hai

_BANNED_TEXT = ('<blockquote>🚫 <b>ʙʟᴏᴄᴋᴇᴅ</b>\n'
                'You are blocked from using this bot!\n'
                '📩 Contact Admin: @notCoder2006</blockquote>')

def _maint_text():
    return ('<blockquote>🛠 <b>ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ</b>\n\n'
            'Dashboard currently under maintenance, please wait.\n'
            'Please wait.\n'
            'This feature will be soon again.\n'
            '⚡ @notCoder2006</blockquote>')

def _parse_uid(text):
    """Telegram User ID: sirf positive number. Invalid => None."""
    t = (text or '').strip()
    if not re.fullmatch(r'\d{5,15}', t):
        return None
    return int(t)

def is_user_banned(uid):
    """Single ban check: blocked_identifiers(user_id) YA users.is_blocked. Owner/admin kabhi banned nahi."""
    try:
        uid = int(uid)
    except Exception:
        return False
    if uid == OWNER_ID or is_admin(uid):
        return False
    try:
        if is_identifier_blocked(str(uid)):
            return True
        r = c.execute('SELECT is_blocked FROM users WHERE user_id=?', (uid,)).fetchone()
        return bool(r and r[0])
    except Exception as e:
        print(f'[BAN_CHECK] {e}')
        return False

def _ban_user(uid, by):
    uid = int(uid)
    block_identifier(str(uid), 'user_id', by, 'Blocked by admin')
    c.execute('UPDATE users SET is_blocked=1 WHERE user_id=?', (uid,))
    conn.commit()

def _unban_user(uid):
    """True agar user pehle blocked tha."""
    uid = int(uid)
    was = is_identifier_blocked(str(uid))
    r = c.execute('SELECT is_blocked FROM users WHERE user_id=?', (uid,)).fetchone()
    if r and r[0]:
        was = True
    unblock_identifier(str(uid))
    c.execute('UPDATE users SET is_blocked=0 WHERE user_id=?', (uid,))
    conn.commit()
    return bool(was)

# ---------------- admin management ----------------
def _user_label(uid):
    try:
        r = c.execute('SELECT username,first_name FROM users WHERE user_id=?', (int(uid),)).fetchone()
        if r:
            if r[0]:
                return '@' + _html.escape(str(r[0]))
            if r[1]:
                return _html.escape(str(r[1]))[:20]
    except Exception:
        pass
    return ''

def _active_admin_ids():
    try:
        rows = c.execute('SELECT user_id FROM admins WHERE is_active=1 ORDER BY user_id').fetchall()
    except Exception:
        rows = []
    return [r[0] for r in rows if r[0] != OWNER_ID]
def _admin_list_text():
    def _row(uid):
        nm = un = ''
        try:
            r = c.execute('SELECT username,first_name FROM users WHERE user_id=?', (int(uid),)).fetchone()
            if r:
                un = ('@' + _html.escape(str(r[0]))) if r[0] else ''
                nm = _html.escape(str(r[1] or ''))[:25]
        except Exception:
            pass
        return f'👤 Name: {nm or "-"}\n🔖 Username: {un or "-"}\n🆔 User ID: <code>{uid}</code>'
    parts = ['👑 <b>Owner</b>\n' + _row(OWNER_ID)]
    for a in _active_admin_ids():
        parts.append('🛡️ <b>Admin</b>\n' + _row(a))
    return '<blockquote>📋 <b>ADMIN LIST</b>\n━━━━━━━━━━━━━━━━\n' + '\n\n'.join(parts) + f'\n━━━━━━━━━━━━━━━━\nTotal: {len(parts)}\n\n✅ Every active Admin gets the full admin panel.</blockquote>'

def _remove_admin(target):
    """(ok, message). Owner reject, non-admin => meaningful message."""
    target = int(target)
    if target == OWNER_ID:
        return False, '⛔ Owner cannot be removed.'
    try:
        if not c.execute('SELECT 1 FROM admins WHERE user_id=? AND is_active=1', (target,)).fetchone():
            return False, '⚠️ This user is not an active Admin.'
        c.execute('UPDATE admins SET is_active=0 WHERE user_id=?', (target,))
        conn.commit()
        _admin_cache.pop(target, None)
        return True, f'✅ <b>Admin access removed</b>\n🆔 <code>{target}</code>'
    except Exception as e:
        return False, f'❌ Database error: {_safe_err(e)}'

def _remove_admin_menu():
    ids = _active_admin_ids()
    if not ids:
        return '<blockquote>📋 <b>REMOVE ADMIN</b>\n\nNo extra admins found.</blockquote>', None
    mk = InlineKeyboardMarkup()
    for a in ids:
        nm = _user_label(a)
        mk.row(_IKB(f'🛡️ {a}' + (f' {nm}' if nm else ''), style='primary', callback_data='admrm_i'),
               _IKB('REMOVE', style='danger', callback_data=f'admrm_{a}'))
    return '<blockquote>📋 <b>REMOVE ADMIN</b>\nTap REMOVE to remove admin access:</blockquote>', mk

@bot.callback_query_handler(func=lambda call: bool(call.data) and call.data.startswith('admrm_'))
def cb_remove_admin(call):
    uid = call.from_user.id
    try:
        if not is_admin(uid) or (ADMIN_MGMT_OWNER_ONLY and uid != OWNER_ID):
            bot.answer_callback_query(call.id, 'Not allowed!', show_alert=True); return
        arg = call.data[len('admrm_'):]
        if arg == 'i':
            bot.answer_callback_query(call.id); return
        target = _parse_uid(arg)
        if target is None:
            bot.answer_callback_query(call.id, 'Invalid ID', show_alert=True); return
        ok, msg = _remove_admin(target)
        bot.answer_callback_query(call.id, 'Removed ✅' if ok else 'Failed', show_alert=not ok)
        txt, mk = _remove_admin_menu()
        txt = txt.replace('<blockquote>', '<blockquote>' + msg + '\n\n', 1)
        try:
            bot.edit_message_text(txt, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=mk)
        except Exception:
            bot.send_message(call.message.chat.id, txt, parse_mode='HTML', reply_markup=mk)
    except Exception as e:
        print(f'[ADMRM] {e}')

# ---------------- maintenance ----------------
def _maint_menu_text():
    st = 'ON' if is_maintenance() else 'OFF'
    return f'<blockquote>🛠 <b>ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ ᴍᴏᴅᴇ</b>\n\nStatus: <b>{st}</b>\nON hone par sirf admins bot use kar sakte hain.</blockquote>'

def _maint_menu_kb():
    mk = InlineKeyboardMarkup()
    mk.row(_IKB('🔴 ON', style='danger', callback_data='mnt_on'), _IKB('🟢 OFF', style='success', callback_data='mnt_off'))
    return mk

@bot.callback_query_handler(func=lambda call: bool(call.data) and call.data.startswith('mnt_'))
def cb_maintenance(call):
    try:
        if not is_admin(call.from_user.id):
            bot.answer_callback_query(call.id, 'Not allowed!', show_alert=True); return
        want = '1' if call.data == 'mnt_on' else '0'
        if not _set_setting('maintenance', want):
            bot.answer_callback_query(call.id, 'Database error!', show_alert=True); return
        bot.answer_callback_query(call.id, 'Maintenance ' + ('ON' if want == '1' else 'OFF'))
        try:
            bot.edit_message_text(_maint_menu_text(), call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=_maint_menu_kb())
        except Exception:
            pass
    except Exception as e:
        print(f'[MAINT_CB] {e}')

# ---------------- force-join targets (channel / group, public / private) ----------------
_fj_add_state = {}
def kb_fj_type():
    mk = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    mk.row(_KB('📢 CHANNEL', style='primary'), _KB('👥 GROUP', style='primary'))
    mk.row(_KB('❌ CANCEL', style='danger'))
    return mk

def kb_fj_vis():
    mk = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    mk.row(_KB('🌐 PUBLIC', style='success'), _KB('🔒 PRIVATE', style='primary'))
    mk.row(_KB('❌ CANCEL', style='danger'))
    return mk

def kb_fj_cancel():
    mk = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    mk.row(_KB('❌ CANCEL', style='danger'))
    return mk

def _fj_add_start(uid):
    _fj_add_state[uid] = {'step': 'type'}
    try:
        bot.clear_step_handler_by_chat_id(uid)
    except Exception:
        pass
    bot.send_message(uid, '<blockquote>➕ <b>ADD TARGET</b>\nSelect type:</blockquote>', parse_mode='HTML', reply_markup=kb_fj_type())

def _fj_step_is(uid, step):
    st = _fj_add_state.get(uid)
    return bool(st) and st.get('step') == step

@bot.message_handler(func=lambda m: m.text in ['📢 CHANNEL', '👥 GROUP'] and is_admin(m.from_user.id) and _fj_step_is(m.from_user.id, 'type'))
def h_fj_type(m):
    uid = m.from_user.id
    _fj_add_state[uid] = {'step': 'vis', 'type': 'channel' if 'CHANNEL' in m.text else 'group'}
    bot.send_message(m.chat.id, f"<blockquote>➕ <b>ADD {_fj_add_state[uid]['type'].upper()}</b>\nSelect visibility:</blockquote>", parse_mode='HTML', reply_markup=kb_fj_vis())

@bot.message_handler(func=lambda m: m.text in ['🌐 PUBLIC', '🔒 PRIVATE'] and is_admin(m.from_user.id) and _fj_step_is(m.from_user.id, 'vis'))
def h_fj_vis(m):
    uid = m.from_user.id
    st = _fj_add_state[uid]
    st['vis'] = 'public' if 'PUBLIC' in m.text else 'private'
    st['step'] = 'chatid'
    bot.register_next_step_handler(bot.send_message(m.chat.id, '<blockquote>🆔 Send <b>Chat ID</b> (compulsory):\n<code>-100xxxxxxxxxx</code></blockquote>', parse_mode='HTML', reply_markup=kb_fj_cancel()), _fj_add_chatid)

@bot.message_handler(func=lambda m: m.text == '❌ CANCEL' and is_admin(m.from_user.id))
def h_fj_cancel(m):
    _fj_add_state.pop(m.from_user.id, None)
    try:
        bot.clear_step_handler_by_chat_id(m.chat.id)
    except Exception:
        pass
    bot.send_message(m.chat.id, '<blockquote>❌ Cancelled.</blockquote>', parse_mode='HTML', reply_markup=kb_channel_mgmt())

def _fj_fail(chat_id, text):
    try:
        bot.send_message(chat_id, f'<blockquote>❌ {text}</blockquote>', parse_mode='HTML', reply_markup=kb_channel_mgmt())
    except Exception:
        pass

@bot.callback_query_handler(func=lambda call: bool(call.data) and call.data.startswith('fjadd_'))
def cb_fj_add(call):
    uid = call.from_user.id
    try:
        if not is_admin(uid):
            bot.answer_callback_query(call.id, 'Not allowed!', show_alert=True); return
        d = call.data
        bot.answer_callback_query(call.id)
        if d == 'fjadd_cancel':
            _fj_add_state.pop(uid, None)
            bot.clear_step_handler_by_chat_id(uid) if hasattr(bot, 'clear_step_handler_by_chat_id') else None
            bot.send_message(uid, '<blockquote>❌ Cancelled.</blockquote>', parse_mode='HTML', reply_markup=kb_channel_mgmt()); return
        st = _fj_add_state.setdefault(uid, {})
        if d in ('fjadd_t_channel', 'fjadd_t_group'):
            st.clear(); st['type'] = d.split('_')[-1]
            mk = InlineKeyboardMarkup()
            mk.row(_IKB('🌐 PUBLIC', style='success', callback_data='fjadd_v_public'), _IKB('🔒 PRIVATE', style='primary', callback_data='fjadd_v_private'))
            mk.row(_IKB('❌ CANCEL', style='danger', callback_data='fjadd_cancel'))
            bot.send_message(uid, f"<blockquote>➕ <b>ADD {st['type'].upper()}</b>\nSelect visibility:</blockquote>", parse_mode='HTML', reply_markup=mk)
        elif d in ('fjadd_v_public', 'fjadd_v_private'):
            if 'type' not in st:
                _fj_add_start(uid); return
            st['vis'] = d.split('_')[-1]
            bot.register_next_step_handler_by_chat_id(uid, _fj_add_chatid)
            bot.send_message(uid, '<blockquote>🆔 Send <b>Chat ID</b> (compulsory):\n<code>-100xxxxxxxxxx</code></blockquote>', parse_mode='HTML')
    except Exception as e:
        print(f'[FJADD_CB] {e}')

def _fj_add_chatid(m):
    uid = m.from_user.id
    if not is_admin(uid):
        return
    st = _fj_add_state.get(uid)
    if not st or 'type' not in st or 'vis' not in st:
        _fj_fail(m.chat.id, 'Session expired. ADD CHANNEL se dobara start karo.'); return
    raw = (m.text or '').strip()
    if not re.fullmatch(r'-100\d{5,}', raw):
        _fj_fail(m.chat.id, 'Invalid Chat ID! Format: <code>-100xxxxxxxxxx</code>'); return
    try:
        ch = bot.get_chat(int(raw))
    except Exception as e:
        _fj_fail(m.chat.id, f'Unknown target: chat nahi mila ya bot us chat mein nahi hai.\n<code>{_safe_err(e)}</code>'); return
    ctype = getattr(ch, 'type', '')
    if st['type'] == 'channel' and ctype != 'channel':
        _fj_fail(m.chat.id, 'Ye Chat ID channel ki nahi hai (GROUP try karo).'); return
    if st['type'] == 'group' and ctype not in ('group', 'supergroup'):
        _fj_fail(m.chat.id, 'Ye Chat ID group ki nahi hai (CHANNEL try karo).'); return
    try:
        me = bot.get_me()
        mem = bot.get_chat_member(ch.id, me.id)
        if getattr(mem, 'status', '') not in ('administrator', 'creator'):
            raise ValueError('not admin')
    except Exception:
        _fj_fail(m.chat.id, 'Bot ko is chat mein <b>Admin</b> banao, warna membership verify nahi ho sakti. Phir dobara add karo.'); return
    st['chat_id'] = str(ch.id)
    st['title'] = ch.title or str(ch.id)
    un = getattr(ch, 'username', None)
    if st['vis'] == 'public':
        if not un:
            _fj_fail(m.chat.id, 'Is chat ka public @username nahi hai. PRIVATE select karke invite link do.'); return
        st['url'] = 'https://t.me/' + un
        _fj_save(m.chat.id, uid, st)
    else:
        st['step'] = 'link'
        bot.register_next_step_handler(bot.send_message(m.chat.id, '<blockquote>🔗 Send <b>Invite/Join Link</b>:\n<code>https://t.me/+xxxxxxxx</code></blockquote>', parse_mode='HTML', reply_markup=kb_fj_cancel()), _fj_add_link)

def _fj_add_link(m):
    uid = m.from_user.id
    if not is_admin(uid):
        return
    st = _fj_add_state.get(uid)
    if not st or 'chat_id' not in st:
        _fj_fail(m.chat.id, 'Session expired. ADD CHANNEL se dobara start karo.'); return
    link = (m.text or '').strip()
    if not re.fullmatch(r'https://t\.me/(\+[A-Za-z0-9_-]{6,}|joinchat/[A-Za-z0-9_-]{6,}|[A-Za-z][A-Za-z0-9_]{4,})', link):
        _fj_fail(m.chat.id, 'Private target ke liye valid invite link zaroori hai (<code>https://t.me/+xxxx</code>).'); return
    st['url'] = link
    _fj_save(m.chat.id, uid, st)

def _fj_save(chat_id, uid, st):
    try:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        row = c.execute('SELECT id FROM force_join_channels WHERE chat_id=?', (st['chat_id'],)).fetchone()
        if row:
            c.execute('UPDATE force_join_channels SET chat_title=?,chat_url=?,added_by=?,added_date=?,is_active=1,chat_type=?,visibility=? WHERE id=?',
                      (st['title'], st['url'], uid, now, st['type'], st['vis'], row[0]))
        else:
            c.execute('INSERT INTO force_join_channels(chat_id,chat_title,chat_url,added_by,added_date,is_active,chat_type,visibility) VALUES(?,?,?,?,?,1,?,?)',
                      (st['chat_id'], st['title'], st['url'], uid, now, st['type'], st['vis']))
        conn.commit()
        _channel_check_cache.clear()
        _fj_add_state.pop(uid, None)
        bot.send_message(chat_id, f"<blockquote>✅ <b>{st['type'].upper()} added</b> ({st['vis'].upper()})\n📢 {_html.escape(st['title'])}\n🆔 <code>{st['chat_id']}</code>\n🔗 {_html.escape(st['url'])}</blockquote>", parse_mode='HTML', reply_markup=kb_channel_mgmt())
    except Exception as e:
        _fj_fail(chat_id, f'Database error: {_safe_err(e)}')

def _fj_list_text():
    chs = get_force_join_channels()
    if not chs:
        return '<blockquote>Koi channel nahi hai abhi.\n\nADD CHANNEL se add karo.</blockquote>'
    txt = '<blockquote>📋 <b>Force Join Targets</b>\n' + '─' * 22 + '\n\n'
    for i, entry in enumerate(chs, 1):
        meta = ''
        try:
            r = c.execute('SELECT chat_type,visibility FROM force_join_channels WHERE chat_id=? AND is_active=1', (str(entry[0]),)).fetchone()
            if r:
                meta = f' [{(r[0] or "channel").upper()} / {(r[1] or "public").upper()}]'
        except Exception:
            pass
        txt += f'{i}. <b>{_html.escape(str(entry[1]))}</b>{meta}\n🆔 <code>{entry[0]}</code>\n🔗 {_html.escape(str(entry[2] or ""))}\n\n'
    txt += '─' * 22 + f'\nTotal: {len(chs)}</blockquote>'
    return txt


@bot.message_handler(func=lambda m: m.text in [' REMOVE PREMIUM', 'ʀᴇᴍᴏᴠᴇ ᴩʀᴇᴍɪᴜᴍ'] and is_admin(m.from_user.id))
def h_rem_prem(m):
    bot.register_next_step_handler(bot.reply_to(m, '<blockquote> Send User ID to remove premium:</blockquote>', parse_mode='HTML'), do_rem_prem)

def do_rem_prem(m):
    if not is_admin(m.from_user.id):
        return
    try:
        uid_t = int(m.text.strip())
        c.execute('UPDATE users SET is_premium=0, premium_until=NULL WHERE user_id=?', (uid_t,))
        conn.commit()
        bot.reply_to(m, f'<blockquote>✅ Premium removed from <code>{uid_t}</code></blockquote>', parse_mode='HTML')
        try:
            bot.send_message(uid_t, '<blockquote> Your premium has been removed by admin.\n @notCoder2006</blockquote>', parse_mode='HTML')
        except:
            pass
    except:
        bot.reply_to(m, '<blockquote> Invalid User ID</blockquote>', parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text in [' CHECK CREDITS', 'ᴄʜᴇᴄᴋ ᴄʀᴇᴅɪᴛꜱ'] and is_admin(m.from_user.id))
def h_check_cr(m):
    bot.register_next_step_handler(bot.reply_to(m, '<blockquote> Send User ID to check credits:</blockquote>', parse_mode='HTML'), do_check_cr)

def do_check_cr(m):
    if not is_admin(m.from_user.id):
        return
    try:
        uid_t = int(m.text.strip())
        u = get_user(uid_t)
        if not u:
            bot.reply_to(m, '<blockquote> User not found</blockquote>', parse_mode='HTML')
            return
        cr = u[5]
        prem = 'Yes' if u[7] == 1 else 'No'
        until = u[8] or '—'
        blocked = 'Yes' if u[6] == 1 else 'No'
        refs = get_referral_count(uid_t)
        bot.reply_to(m, f"<blockquote>🔍 <b>USER INFO</b>\n━━━━━━━━━━━━━━━━━━\n🆔 ID: <code>{uid_t}</code>\n👤 Name: {u[2] or '—'}\n🔗 Username: @{u[1] or '—'}\n💰 Credits: <b>{cr}</b>\n💎 Premium: <b>{prem}</b>\n📅 Premium until: {until}\n🚫 Blocked: {blocked}\n👥 Refers: {refs}\n━━━━━━━━━━━━━━━━━━\n⚡ @notCoder2006</blockquote>", parse_mode='HTML')
    except Exception as e:
        bot.reply_to(m, f'<blockquote>❌ {_safe_err(e)}</blockquote>', parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text in [' SCHEDULE BC', 'ꜱᴄʜᴇᴅᴜʟᴇ ʙᴄ'] and is_admin(m.from_user.id))
def h_schedule_bc(m):
    bot.register_next_step_handler(bot.reply_to(m, '<blockquote> Schedule broadcast\nFormat: <code>YYYY-MM-DD HH:MM | message</code>\nExample: <code>2026-09-24 18:30 | Hello everyone!</code></blockquote>', parse_mode='HTML'), do_schedule_bc)

def do_schedule_bc(m):
    if not is_admin(m.from_user.id):
        return
    try:
        raw = m.text.strip()
        if '|' not in raw:
            bot.reply_to(m, '<blockquote> Use: time | message</blockquote>', parse_mode='HTML')
            return
        when, msg = raw.split('|', 1)
        when = when.strip()
        msg = msg.strip()
        datetime.strptime(when, '%Y-%m-%d %H:%M')
        c.execute('INSERT INTO scheduled_broadcasts(message, run_at, status, created_by, created_date) VALUES(?,?,?,?,?)', (msg, when, 'pending', m.from_user.id, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()
        bot.reply_to(m, f'<blockquote>✅ Scheduled!\n🕒 {when}\n📝 {msg[:80]}</blockquote>', parse_mode='HTML')
    except Exception as e:
        bot.reply_to(m, f'<blockquote>❌ {_safe_err(e)}</blockquote>', parse_mode='HTML')

def _scheduler_loop():
    while True:
        try:
            time.sleep(30)
            now = datetime.now().strftime('%Y-%m-%d %H:%M')
            rows = c.execute("SELECT id, message FROM scheduled_broadcasts WHERE status='pending' AND run_at<=?", (now,)).fetchall()
            for sid, msg in rows:
                c.execute("UPDATE scheduled_broadcasts SET status='running' WHERE id=?", (sid,))
                conn.commit()
                users = c.execute('SELECT user_id FROM users WHERE is_blocked=0').fetchall()
                ok = fail = 0
                for uid_t, in users:
                    try:
                        bot.send_message(uid_t, f'<blockquote>{msg}</blockquote>', parse_mode='HTML')
                        ok += 1
                        time.sleep(0.05)
                    except:
                        fail += 1
                c.execute('UPDATE scheduled_broadcasts SET status=? WHERE id=?', (f'done ok={ok} fail={fail}', sid))
                conn.commit()
                try:
                    bot.send_message(OWNER_ID, f'<blockquote>⏰ Scheduled BC done\n✅ {ok} ❌ {fail}</blockquote>', parse_mode='HTML')
                except:
                    pass
        except Exception as e:
            print('[SCHEDULER]', e)
            time.sleep(60)
try:
    threading.Thread(target=_scheduler_loop, daemon=True).start()
except:
    pass

@bot.message_handler(content_types=['users_shared'])
def h_user_shared(m):
    uid = m.from_user.id
    user = get_user(uid)
    if not user or not m.users_shared or (not m.users_shared.user_ids):
        return
    if user[6] == 1:
        bot.reply_to(m, '<blockquote> You are blocked!</blockquote>', parse_mode='HTML')
        return
    if not check_channel(uid):
        mk = get_channels_keyboard(uid)
        if mk:
            bot.reply_to(m, format_force_join_msg(), reply_markup=mk, parse_mode='HTML')
            return
    if user[5] <= 0 and (not is_admin(uid)) and (user[7] != 1):
        txt, mk = no_credits_msg(uid)
        bot.reply_to(m, txt, reply_markup=mk, parse_mode='HTML')
        return
    _raw_obj = m.users_shared.user_ids[0]
    if hasattr(_raw_obj, 'user_id'):
        raw = _raw_obj.user_id
    elif isinstance(_raw_obj, dict):
        raw = _raw_obj.get('user_id') or _raw_obj.get('id')
    else:
        raw = _raw_obj
    try:
        raw = int(raw)
    except:
        bot.send_message(uid, '<blockquote> User ID detect nahi hua!\n @notCoder2006</blockquote>', parse_mode='HTML')
        return
    ld = bot.send_message(uid, '<blockquote>' + pbar(5) + '\n ꜰᴇᴛᴄʜɪɴɢ ᴀʟʟ ᴅᴀᴛᴀ...</blockquote>', parse_mode='HTML')
    deduct_credit(uid)
    stop_sel = _start_anim(uid, ld.message_id, 'usernum')
    import concurrent.futures as _cfu_sel
    try:
        with _cfu_sel.ThreadPoolExecutor(max_workers=1) as _ex_sel:
            _fut_sel = _ex_sel.submit(api_full_user, str(raw))
            res = _fut_sel.result(timeout=45)
    except Exception:
        res = None
    stop_sel[0] = True
    pic = None
    if res:
        pic = res.get('profile_pic') or res.get('profile_picture')
    if not pic:
        pic = f'http://username-to-info-rwsw.onrender.com/media/{raw}.png'
    _tg_pic = _fetch_pfp_by_id(str(raw))
    if _tg_pic:
        pic = _tg_pic
    now = _now_ist()
    if res and res.get('success'):
        ud2 = res.get('data', {}) or {}
        _un2_raw = ud2.get('username') or res.get('username') or res.get('target_username') or ''
        un2 = _un2_raw.replace('@', '').strip() if isinstance(_un2_raw, str) else ''
        label = f'@{un2} | {raw}' if un2 else f'User ID: {raw}'
        _cr_left_su = get_credits(uid)
        txt, _ = _fmt_tg_user(res, '', 'SELECTED USER', label, now, _cr_left_su)
        try:
            bot.edit_message_text(txt, uid, ld.message_id, parse_mode='HTML')
        except:
            bot.send_message(uid, txt, parse_mode='HTML')
        bot.send_message(uid, '<blockquote>⬇ ᴍᴀɪɴ ᴍᴇɴᴜ</blockquote>', reply_markup=kb_p1(uid), parse_mode='HTML')
        c.execute('INSERT INTO search_history(user_id,search_type,query,search_date,result) VALUES(?,?,?,?,?)', (uid, 'user_id', str(raw), datetime.now().strftime('%Y-%m-%d %H:%M:%S'), json.dumps(res)))
        conn.commit()
        log_search(uid, m.from_user.first_name or 'User', m.from_user.username or '', 'SELECT USER', str(raw), None)
    else:
        if not is_admin(uid) and user[7] != 1:
            refund_credit(uid)
        tg_direct = _fetch_tg_user_direct(str(raw))
        fn = tg_direct.get('first_name', '') or ''
        ln = tg_direct.get('last_name', '') or ''
        un2 = tg_direct.get('username', '') or ''
        label = f'@{un2} | {raw}' if un2 else f'User ID: {raw}'
        minimal_res = {'success': bool(fn or un2), 'phone': 'N/A', 'telegram_id': str(raw), 'target_id': str(raw), 'country': '—', 'country_code': '', 'data': {'first_name': fn, 'last_name': ln, 'username': un2, 'telegram_id': str(raw), 'bio': tg_direct.get('bio', '') or ''}}
        _cr_left_su2 = get_credits(uid)
        err, _ = _fmt_tg_user(minimal_res, '', 'SELECTED USER', label, now, _cr_left_su2)
        try:
            bot.edit_message_text(err, uid, ld.message_id, parse_mode='HTML')
        except:
            bot.send_message(uid, err, parse_mode='HTML')
        bot.send_message(uid, '<blockquote>⬇ ᴍᴀɪɴ ᴍᴇɴᴜ</blockquote>', reply_markup=kb_p1(uid), parse_mode='HTML')

@bot.channel_post_handler(func=lambda m: True)
def h_channel_post(m):
    """Channel posts — bot bilkul respond nahi karega"""
    return

@bot.message_handler(func=lambda m: m.chat.type in ['group', 'supergroup', 'channel'])
def h_group(m):
    """Group: number/username auto-detect + /like /info /bomb /stopbomb /user commands"""
    if m.chat.type == 'channel':
        return
    cid = m.chat.id
    uid = m.from_user.id
    txt = (m.text or '').strip()
    if not txt:
        return
    add_group_to_db(cid, m.chat.title or 'Unknown', uid)
    fname = _html.escape(m.from_user.first_name or 'User')
    uname = m.from_user.username or ''
    _fj_skip_cmds = ['/start', '/wel', '/weloff', '/setrules']
    _is_skip = any((txt.startswith(cc) for cc in _fj_skip_cmds))
    _is_real_search = bool(re.match('^[6-9]\\d{9}$', txt)) or bool(re.match('^@[a-zA-Z0-9_.]{4,}$', txt)) or any((txt.startswith(x) for x in ['/bomb', '/like', '/info', '/user', '/insta', '/spin', '/freespin']))
    if not _is_skip and _is_real_search and (not is_admin(uid)):
        _user_grp = get_user(uid)
        if not _user_grp:
            add_user(uid, uname, fname)
            _user_grp = get_user(uid)
        if not check_channel(uid):
            _mk_fj2 = get_channels_keyboard(uid)
            if _mk_fj2:
                try:
                    bot.reply_to(m, format_force_join_msg(), reply_markup=_mk_fj2, parse_mode='HTML')
                except:
                    pass
            return
    if txt.startswith('/freespin') or txt.startswith('/spin'):
        if check_blocked_and_reply(uid):
            return
        threading.Thread(target=_do_group_spin, args=(uid, fname, uname, cid), daemon=True).start()
        return
    if txt.startswith('/bomb'):
        if not False:
            bot.reply_to(m, '<blockquote>━━━━━━━━━━━━━━━━━━\n ᴛʜɪꜱ ꜰᴇᴀᴛᴜʀᴇ ɪꜱ ᴜɴᴅᴇʀ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ\n━━━━━━━━━━━━━━━━━━\n System maintenance\n ᴛʜᴏᴅɪ ᴅᴇʀ ᴍᴇɪɴ ᴡᴀᴩᴀꜱ ᴀᴀ ᴊᴀᴇɢᴀ!\n━━━━━━━━━━━━━━━━━━\n ᴅᴇᴠᴇʟᴏᴩᴇʀ : @notCoder2006</blockquote>', parse_mode='HTML')
            return
        parts = txt.split()
        num = re.sub('\\D', '', parts[1]) if len(parts) > 1 else ''
        if len(num) == 12 and num.startswith('91'):
            num = num[2:]
        if not re.match('^[6-9]\\d{9}$', num):
            bot.reply_to(m, '<blockquote> Usage: <code>/bomb 9876543210</code></blockquote>', parse_mode='HTML')
            return
        if bomber_jobs.get(uid, {}).get('running', False):
            bot.reply_to(m, '<blockquote> Already running! Use /stopbomb</blockquote>', parse_mode='HTML')
            return
        if not is_admin(uid):
            _ucr_b = get_credits(uid)
            try:
                _ucr_b_int = int(_ucr_b) if _ucr_b != '∞' else 999
            except:
                _ucr_b_int = 0
            if _ucr_b_int <= 0:
                _nc_t, _nc_m = no_credits_msg(uid)
                try:
                    bot.reply_to(m, _nc_t, reply_markup=_nc_m, parse_mode='HTML')
                except:
                    bot.send_message(cid, _nc_t, reply_markup=_nc_m, parse_mode='HTML')
                return
        sm = bot.reply_to(m, '<blockquote>' + pbar(0) + '\nꜱᴛᴀʀᴛɪɴɢ...</blockquote>', parse_mode='HTML')
        try:
            bot.send_chat_action(cid, 'typing')
        except:
            pass
        _start_anim(cid, sm.message_id, 'bomber')
        threading.Thread(target=run_bomber, args=(uid, cid, num, sm.message_id), daemon=True).start()
        return
    if txt.startswith('/stopbomb'):
        if uid in bomber_jobs:
            bomber_jobs[uid]['running'] = False
        bot.reply_to(m, '<blockquote> <b>Bomber stopped!</b></blockquote>', parse_mode='HTML')
        return
    if txt.startswith('/like'):
        if not False:
            bot.reply_to(m, '<blockquote>━━━━━━━━━━━━━━━━━━\n ᴛʜɪꜱ ꜰᴇᴀᴛᴜʀᴇ ɪꜱ ᴜɴᴅᴇʀ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ\n━━━━━━━━━━━━━━━━━━\n System maintenance\n ᴛʜᴏᴅɪ ᴅᴇʀ ᴍᴇɪɴ ᴡᴀᴩᴀꜱ ᴀᴀ ᴊᴀᴇɢᴀ!\n━━━━━━━━━━━━━━━━━━\n ᴅᴇᴠᴇʟᴏᴩᴇʀ : @notCoder2006</blockquote>', parse_mode='HTML')
            return
        parts = txt.split()
        ff_uid = re.sub('\\D', '', parts[-1]) if len(parts) > 1 else ''
        if len(ff_uid) < 5:
            bot.reply_to(m, '<blockquote> Usage: <code>/like 2819649271</code></blockquote>', parse_mode='HTML')
            return
        if not is_admin(uid) and int(get_credits(uid) if get_credits(uid) != '∞' else 999) <= 0:
            _nc_txt, _nc_mk = no_credits_msg(uid)
            try:
                bot.reply_to(m, _nc_txt, reply_markup=_nc_mk, parse_mode='HTML')
            except:
                bot.send_message(cid, _nc_txt, reply_markup=_nc_mk, parse_mode='HTML')
            return
        try:
            bot.send_chat_action(cid, 'playing')
        except:
            pass
        sm = bot.reply_to(m, '<blockquote>' + pbar(0) + '\nꜱᴛᴀʀᴛɪɴɢ...</blockquote>', parse_mode='HTML')
        try:
            bot.send_chat_action(cid, 'typing')
        except:
            pass
        threading.Thread(target=do_ff_like_send, args=(cid, sm.message_id, ff_uid, 'ind', uid, fname), daemon=True).start()
        return
    if txt.startswith('/info'):
        if not False:
            bot.reply_to(m, '<blockquote>━━━━━━━━━━━━━━━━━━\n ᴛʜɪꜱ ꜰᴇᴀᴛᴜʀᴇ ɪꜱ ᴜɴᴅᴇʀ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ\n━━━━━━━━━━━━━━━━━━\n System maintenance\n ᴛʜᴏᴅɪ ᴅᴇʀ ᴍᴇɪɴ ᴡᴀᴩᴀꜱ ᴀᴀ ᴊᴀᴇɢᴀ!\n━━━━━━━━━━━━━━━━━━\n ᴅᴇᴠᴇʟᴏᴩᴇʀ : @notCoder2006</blockquote>', parse_mode='HTML')
            return
        if is_group_muted(cid):
            return
        g = get_group(cid)
        if safe_g(g, 6) == 1 if g else False:
            return
        parts = txt.split()
        ff_uid = re.sub('\\D', '', parts[-1]) if len(parts) > 1 else ''
        if len(ff_uid) < 5:
            return
        if not deduct_credit(uid, 1, cid):
            _nc_txt, _nc_mk = no_credits_msg(uid)
            try:
                bot.reply_to(m, _nc_txt, reply_markup=_nc_mk, parse_mode='HTML')
            except:
                bot.send_message(cid, _nc_txt, reply_markup=_nc_mk, parse_mode='HTML')
            return
        sm = bot.reply_to(m, '<blockquote>' + pbar(0) + '\nꜱᴛᴀʀᴛɪɴɢ...</blockquote>', parse_mode='HTML')
        try:
            bot.send_chat_action(cid, 'typing')
        except:
            pass
        _sf_gif = _start_anim(cid, sm.message_id, 'freefire')
        res = api_ff(ff_uid)
        _sf_gif[0] = True
        p1, p2 = fmt_ff(res, ff_uid, fname)
        try:
            bot.edit_message_text(p1, cid, sm.message_id, parse_mode='HTML')
        except:
            bot.send_message(cid, p1, parse_mode='HTML')
        if p2:
            bot.send_message(cid, p2, parse_mode='HTML')
        if not (res and res.get('success')):
            refund_credit(uid, 1)
        return
    if txt.startswith('/user'):
        if not is_feature_enabled('tgid'):
            bot.reply_to(m, '<blockquote>━━━━━━━━━━━━━━━━━━\n ᴛʜɪꜱ ꜰᴇᴀᴛᴜʀᴇ ɪꜱ ᴜɴᴅᴇʀ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ\n━━━━━━━━━━━━━━━━━━\n System maintenance\n ᴛʜᴏᴅɪ ᴅᴇʀ ᴍᴇɪɴ ᴡᴀᴩᴀꜱ ᴀᴀ ᴊᴀᴇɢᴀ!\n━━━━━━━━━━━━━━━━━━\n ᴅᴇᴠᴇʟᴏᴩᴇʀ : @notCoder2006</blockquote>', parse_mode='HTML')
            return
        if is_group_muted(cid):
            return
        g = get_group(cid)
        if g and safe_g(g, 6) == 1:
            return
        parts = txt.split()
        qid = re.sub('\\D', '', parts[-1]) if len(parts) > 1 else ''
        if len(qid) < 5:
            return
        if not deduct_credit(uid, 1, cid):
            _nc_txt, _nc_mk = no_credits_msg(uid)
            try:
                bot.reply_to(m, _nc_txt, reply_markup=_nc_mk, parse_mode='HTML')
            except:
                bot.send_message(cid, _nc_txt, reply_markup=_nc_mk, parse_mode='HTML')
            return
        sm = bot.reply_to(m, '<blockquote>' + pbar(0) + '\nꜱᴛᴀʀᴛɪɴɢ...</blockquote>', parse_mode='HTML')
        try:
            bot.send_chat_action(cid, 'typing')
        except:
            pass
        _sf_gus = _start_anim(cid, sm.message_id, 'tgid')
        res = api_userid(qid)
        _sf_gus[0] = True
        _cr_left_gus = get_credits(uid)
        rtxt, _ = _fmt_tg_user(res, '', 'TG ID INFO', f'ID: {qid}', _now_ist(), _cr_left_gus)
        try:
            bot.edit_message_text(rtxt, cid, sm.message_id, parse_mode='HTML')
        except:
            bot.send_message(cid, rtxt, parse_mode='HTML')
        if not (res and res.get('success')):
            refund_credit(uid, 1)
        return
    if txt.startswith('/insta'):
        if not False:
            bot.reply_to(m, '<blockquote>━━━━━━━━━━━━━━━━━━\n ᴛʜɪꜱ ꜰᴇᴀᴛᴜʀᴇ ɪꜱ ᴜɴᴅᴇʀ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ\n━━━━━━━━━━━━━━━━━━\n System maintenance\n ᴛʜᴏᴅɪ ᴅᴇʀ ᴍᴇɪɴ ᴡᴀᴩᴀꜱ ᴀᴀ ᴊᴀᴇɢᴀ!\n━━━━━━━━━━━━━━━━━━\n ᴅᴇᴠᴇʟᴏᴩᴇʀ : @notCoder2006</blockquote>', parse_mode='HTML')
            return
        if is_group_muted(cid):
            return
        g = get_group(cid)
        if g and safe_g(g, 6) == 1:
            return
        parts = txt.split()
        insta_id = parts[-1].replace('@', '').strip() if len(parts) > 1 else ''
        if not insta_id or not re.match('^[a-zA-Z0-9_.]{1,30}$', insta_id):
            bot.reply_to(m, '<blockquote> Usage: <code>/insta username</code>\nExample: <code>/insta 𝙽𝚘𝚝 𝙲𝚘𝚍𝚎𝚛bhai</code></blockquote>', parse_mode='HTML')
            return
        if not deduct_credit(uid, 1, cid):
            _nc_txt, _nc_mk = no_credits_msg(uid)
            try:
                bot.reply_to(m, _nc_txt, reply_markup=_nc_mk, parse_mode='HTML')
            except:
                bot.send_message(cid, _nc_txt, reply_markup=_nc_mk, parse_mode='HTML')
            return
        sm = bot.reply_to(m, '<blockquote>' + pbar(0) + '\nꜱᴛᴀʀᴛɪɴɢ...</blockquote>', parse_mode='HTML')
        try:
            bot.send_chat_action(cid, 'typing')
        except:
            pass
        _sf_gin = _start_anim(cid, sm.message_id, 'instagram')
        res = api_instagram(insta_id)
        _sf_gin[0] = True
        rtxt, pic = fmt_instagram(res, insta_id, fname)
        send_with_pfp(cid, rtxt, pic, sm.message_id)
        if res and res.get('success'):
            log_search(uid, fname, uname, 'INSTAGRAM(GRP)', insta_id, pic)
        else:
            refund_credit(uid, 1)
        return
    st_data = user_state.get(uid)
    if isinstance(st_data, dict) and st_data.get('group') and (st_data.get('chat_id') == cid) and (st_data.get('requester') == uid):
        st = st_data.get('state')
        ask_id = st_data.get('ask_id')
        try:
            bot.delete_message(cid, ask_id)
        except:
            pass
        user_state.pop(uid, None)
        if st == S_NUM:
            num = re.sub('\\D', '', txt)
            if len(num) == 12 and num.startswith('91'):
                num = num[2:]
            if not re.match('^[6-9]\\d{9}$', num):
                bot.reply_to(m, '<blockquote> Invalid! 10-digit Indian number bhejo.\n @notCoder2006</blockquote>', parse_mode='HTML')
                return
            if not deduct_credit(uid, 1, cid):
                _nc_t, _nc_m = no_credits_msg(uid)
                try:
                    bot.reply_to(m, _nc_t, reply_markup=_nc_m, parse_mode='HTML')
                except:
                    bot.send_message(cid, _nc_t, reply_markup=_nc_m, parse_mode='HTML')
                return
            ld = bot.reply_to(m, '<blockquote>' + pbar(0) + '\n ꜰᴇᴛᴄʜɪɴɢ...</blockquote>', parse_mode='HTML')
            _t0 = time.time()
            res = api_number(num)
            _elapsed = time.time() - _t0
            _send_number_result(cid, ld.message_id, res, num, uid, _elapsed, edit=True)
            if res and res.get('success'):
                log_search(uid, fname, uname, 'NUMBER(GRP)', num)
            else:
                refund_credit(uid, 1)
            return
        elif st == S_USER:
            un = txt if txt.startswith('@') else '@' + txt
            if not deduct_credit(uid, 1, cid):
                _nc_t, _nc_m = no_credits_msg(uid)
                try:
                    bot.reply_to(m, _nc_t, reply_markup=_nc_m, parse_mode='HTML')
                except:
                    bot.send_message(cid, _nc_t, reply_markup=_nc_m, parse_mode='HTML')
                return
            ld = bot.reply_to(m, '<blockquote>' + pbar(0) + '\n ꜰᴇᴛᴄʜɪɴɢ...</blockquote>', parse_mode='HTML')
            import concurrent.futures as _cfu_gbs
            try:
                with _cfu_gbs.ThreadPoolExecutor(max_workers=1) as _ex_gbs:
                    res = _ex_gbs.submit(api_full_user, un).result(timeout=30)
            except Exception:
                res = None
            now = _now_ist()
            _cr_left_gbs = get_credits(uid) if not is_admin(uid) else '∞'
            rtxt, _ = _fmt_tg_user_short(res, un, now, _cr_left_gbs)
            try:
                bot.edit_message_text(rtxt, cid, ld.message_id, parse_mode='HTML')
            except:
                bot.send_message(cid, rtxt, parse_mode='HTML')
            if res and res.get('success'):
                log_search(uid, fname, uname, 'USERNAME(GRP)', un, None)
            else:
                refund_credit(uid, 1)
            return
        elif st == S_INSTA:
            insta_id = txt.replace('@', '').strip()
            if not re.match('^[a-zA-Z0-9_.]{1,30}$', insta_id):
                bot.reply_to(m, '<blockquote> Invalid Instagram username!\n @notCoder2006</blockquote>', parse_mode='HTML')
                return
            if not deduct_credit(uid, 1, cid):
                _nc_t, _nc_m = no_credits_msg(uid)
                try:
                    bot.reply_to(m, _nc_t, reply_markup=_nc_m, parse_mode='HTML')
                except:
                    bot.send_message(cid, _nc_t, reply_markup=_nc_m, parse_mode='HTML')
                return
            ld = bot.reply_to(m, '<blockquote>' + pbar(0) + '\n ꜰᴇᴛᴄʜɪɴɢ ɪɴꜱᴛᴀ...</blockquote>', parse_mode='HTML')
            res = api_instagram(insta_id)
            rtxt, pic = fmt_instagram(res, insta_id, fname)
            send_with_pfp(cid, rtxt, pic, ld.message_id)
            if res and res.get('success'):
                log_search(uid, fname, uname, 'INSTAGRAM(GRP)', insta_id, pic)
            else:
                refund_credit(uid, 1)
            return
        elif st == S_BOMB:
            num = re.sub('\\D', '', txt)
            if len(num) == 12 and num.startswith('91'):
                num = num[2:]
            if not re.match('^[6-9]\\d{9}$', num):
                bot.reply_to(m, '<blockquote> Invalid! 10-digit number bhejo.\n @notCoder2006</blockquote>', parse_mode='HTML')
                return
            if bomber_jobs.get(uid, {}).get('running', False):
                bot.reply_to(m, '<blockquote> Already running! /stopbomb use karo.\n @notCoder2006</blockquote>', parse_mode='HTML')
                return
            if not deduct_credit(uid, 1, cid):
                _nc_t, _nc_m = no_credits_msg(uid)
                try:
                    bot.reply_to(m, _nc_t, reply_markup=_nc_m, parse_mode='HTML')
                except:
                    bot.send_message(cid, _nc_t, reply_markup=_nc_m, parse_mode='HTML')
                return
            sm = bot.reply_to(m, '<blockquote>' + pbar(0) + '\nꜱᴛᴀʀᴛɪɴɢ...</blockquote>', parse_mode='HTML')
            try:
                bot.send_chat_action(cid, 'typing')
            except:
                pass
            _start_anim(cid, sm.message_id, 'bomber')
            threading.Thread(target=run_bomber, args=(uid, cid, num, sm.message_id), daemon=True).start()
            return
    if txt.startswith('/balance') or txt.startswith('/bal') or txt.startswith('/credits') or txt.startswith('/mybalance'):
        _target_uid = uid
        _target_fname = fname
        _target_uname = uname
        _is_self = True
        if m.reply_to_message and m.reply_to_message.from_user:
            _ru = m.reply_to_message.from_user
            if not _ru.is_bot:
                _target_uid = _ru.id
                _target_fname = _ru.first_name or 'User'
                _target_uname = _ru.username or ''
                _is_self = _target_uid == uid
                add_user(_target_uid, _target_uname, _target_fname)
        add_user(uid, uname, fname)
        _cr = get_credits(_target_uid)
        _ref_cnt = get_referral_count(_target_uid)
        try:
            _coins_t = c.execute('SELECT coins FROM users WHERE user_id=?', (_target_uid,)).fetchone()
            _coins_t = _coins_t[0] if _coins_t else 0
        except:
            _coins_t = 0
        try:
            _row = c.execute('SELECT is_premium,premium_until FROM users WHERE user_id=?', (_target_uid,)).fetchone()
            if _row and _row[0] == 1 and _row[1]:
                try:
                    _exp = datetime.strptime(_row[1], '%Y-%m-%d %H:%M:%S')
                    _pt = ' Premium' if _exp > datetime.now() else ' Free User'
                    _pe = f'Expires: <code>{_row[1]}</code>' if _exp > datetime.now() else 'Expired'
                except:
                    _pt = ' Premium'
                    _pe = ''
            elif _row and _row[0] == 1:
                _pt = ' Premium'
                _pe = ''
            else:
                _pt = ' Free User'
                _pe = ''
        except:
            _pt = ' Free User'
            _pe = ''
        if is_admin(_target_uid):
            _pt = ' Bot Owner'
            _pe = ''
        try:
            _urow = c.execute('SELECT join_date FROM users WHERE user_id=?', (_target_uid,)).fetchone()
            _jd = _urow[0] if _urow and _urow[0] else '—'
        except:
            _jd = '—'
        _uname_bal = f'@{_target_uname}' if _target_uname else 'No Username'
        _title = 'MY BALANCE' if _is_self else 'USER BALANCE'

        def _pb(eid, fb):
            return f"{fb}"
        _L = _pb('5465629669829128119', '') * 10
        _SM = _pb('6147464060305676048', '')
        _CK = _pb('6147565374289220368', '')
        _bal_txt = f"<blockquote>{_L}\n{_pb('6179428482527793899', '')} <b>{_title}</b>\n{_L}\n\n{_pb('5373012449597335010', '')} ɴᴀᴍᴇ    : <a href='tg://user?id={_target_uid}'><b>{_target_fname}</b></a>\n{_pb('5888781182249738113', '')} ɪᴅ      : <code>{_target_uid}</code>\n{_pb('5470135030393090150', '')} ᴜꜱᴇʀɴᴀᴍᴇ: {_uname_bal}\n\n{_L}\n⚡ ᴄʀᴇᴅɪᴛꜱ  : <b>{_cr}</b>\n🎫 ʀᴇꜰᴇʀ ᴘᴛꜱ: <b>{_coins_t}</b>\n{_pb('5465300082628763143', '')} ʀᴇꜰᴇʀʀᴀʟꜱ: <b>{_ref_cnt}</b>\n\n🏅 ꜱᴛᴀᴛᴜꜱ   : {_pt}\n" + (f"{_pb('6242308461598610637', '')} {_pe}\n" if _pe else '') + f"{_pb('6242308461598610637', '')} ᴊᴏɪɴᴇᴅ   : {_jd}\n{_L}\n📤 Refer karo → +{get_referral_bonus()} Credits + 1 Point 🎫\n{_SM} @notCoder2006 {_CK}\n{_L}</blockquote>"
        try:
            bot.reply_to(m, _bal_txt, parse_mode='HTML')
        except:
            bot.send_message(cid, _bal_txt, parse_mode='HTML')
        return
    if txt.startswith('/wel'):
        try:
            _cm = bot.get_chat_member(cid, uid)
            if _cm.status not in ['administrator', 'creator'] and (not is_admin(uid)):
                bot.reply_to(m, '<blockquote> Sirf <b>group admin</b> use kar sakta hai!\n @notCoder2006</blockquote>', parse_mode='HTML')
                return
        except:
            return
        _parts = txt.split()
        _arg = _parts[1].lower() if len(_parts) > 1 else ''
        if _arg == 'off':
            set_group_welcome_on(cid, 0)
            bot.reply_to(m, f"<blockquote>🔕 <b>Welcome Message OFF</b>\n\n❌ Ab naye members ka welcome nahi aayega.\n\n👑 Admin: <a href='tg://user?id={uid}'>{fname}</a>\n💡 ON: <code>/wel on</code>\n⚡ @notCoder2006</blockquote>", parse_mode='HTML')
        elif _arg == 'on':
            set_group_welcome_on(cid, 1)
            bot.reply_to(m, f"<blockquote>🔔 <b>Welcome Message ON</b>\n\n✅ Ab naye members ka welcome aayega! 🎉\n\n👑 Admin: <a href='tg://user?id={uid}'>{fname}</a>\n💡 OFF: <code>/wel off</code>\n⚡ @notCoder2006</blockquote>", parse_mode='HTML')
        else:
            try:
                _wr = c.execute('SELECT bye_on,welcome_on FROM group_welcome_settings WHERE group_id=?', (cid,)).fetchone()
                _ws = ' ON' if _wr and _wr[1] == 1 else ' OFF'
                _bs = ' ON' if _wr and _wr[0] == 1 else ' OFF'
            except:
                _ws = ' OFF'
                _bs = ' OFF'
            bot.reply_to(m, f'<blockquote>ℹ️ <b>Group Settings</b>\n\n👋 Welcome: {_ws}\n🚪 Leave  : {_bs}\n\n• <code>/wel on</code> / <code>/wel off</code>\n• <code>/leave on</code> / <code>/leave off</code>\n⚡ @notCoder2006</blockquote>', parse_mode='HTML')
        return
    if txt.startswith('/leave'):
        try:
            _cm = bot.get_chat_member(cid, uid)
            if _cm.status not in ['administrator', 'creator'] and (not is_admin(uid)):
                bot.reply_to(m, '<blockquote> Sirf <b>group admin</b> use kar sakta hai!\n @notCoder2006</blockquote>', parse_mode='HTML')
                return
        except:
            return
        _parts = txt.split()
        _arg = _parts[1].lower() if len(_parts) > 1 else ''
        if _arg == 'off':
            set_group_bye_on(cid, 0)
            bot.reply_to(m, f"<blockquote>🔕 <b>Leave Message OFF</b>\n\n❌ Ab koi member chhodega toh msg nahi aayega.\n\n👑 Admin: <a href='tg://user?id={uid}'>{fname}</a>\n💡 ON: <code>/leave on</code>\n⚡ @notCoder2006</blockquote>", parse_mode='HTML')
        elif _arg == 'on':
            set_group_bye_on(cid, 1)
            bot.reply_to(m, f"<blockquote>🔔 <b>Leave Message ON</b>\n\n✅ Ab jab koi member chhodega toh msg aayega! 👋\n\n👑 Admin: <a href='tg://user?id={uid}'>{fname}</a>\n💡 OFF: <code>/leave off</code>\n⚡ @notCoder2006</blockquote>", parse_mode='HTML')
        else:
            try:
                _wr = c.execute('SELECT bye_on,welcome_on FROM group_welcome_settings WHERE group_id=?', (cid,)).fetchone()
                _ws = ' ON' if _wr and _wr[1] == 1 else ' OFF'
                _bs = ' ON' if _wr and _wr[0] == 1 else ' OFF'
            except:
                _ws = ' OFF'
                _bs = ' OFF'
            bot.reply_to(m, f'<blockquote>ℹ️ <b>Group Settings</b>\n\n👋 Welcome: {_ws}\n🚪 Leave  : {_bs}\n\n• <code>/wel on</code> / <code>/wel off</code>\n• <code>/leave on</code> / <code>/leave off</code>\n⚡ @notCoder2006</blockquote>', parse_mode='HTML')
        return
    if txt.startswith('/'):
        if txt.startswith('/help') or txt.startswith('/start'):
            if check_blocked_and_reply(uid):
                return
            _cr_g = get_credits(uid)
            _cr_disp = '∞' if is_admin(uid) else str(_cr_g)
            try:
                _ref_g = f'https://t.me/{_get_bot_username()}?start={uid}'
            except:
                _ref_g = f'https://t.me/bot?start={uid}'
            _sep = '━━━━━━━━━━━━━━━━━━'
            _help_txt = f'<blockquote>{_sep}\n🤖 <b>ɢʀᴏᴜᴩ ᴄᴏᴍᴍᴀɴᴅꜱ</b>\n{_sep}\n\n💰 ᴄʀᴇᴅɪᴛꜱ: <b>{_cr_disp}</b>  |  1 ꜱᴇᴀʀᴄʜ = 1 ᴄʀᴇᴅɪᴛ\n\n{_sep}\n📱 <b>SEARCH</b>\n• 9876543210 — Number Info\n• @username — Username Info\n\n🎮 <b>FREE FIRE</b>\n• /info [uid] — FF Player Info\n• /like [uid] — FF Likes\n\n🆔 <b>TG INFO</b>\n• /user [userid] — TG User Info\n\n📸 <b>INSTAGRAM</b>\n• /insta [username] — Insta Info\n\n💣 <b>BOMBER</b>\n• /bomb [number] — Start Bomber\n• /stopbomb — Stop Bomber\n\n🎁 <b>DAILY SPIN</b>\n• /spin — Daily Spin (credits kamao)\n\n{_sep}\n📤 ᴄʀᴇᴅɪᴛꜱ ᴋʜᴀᴛᴀᴍ? Refer karo:\n{_ref_g}\n{_sep}\n⚡ @notCoder2006</blockquote>'
            try:
                bot.reply_to(m, _help_txt, parse_mode='HTML')
            except:
                bot.send_message(cid, _help_txt, parse_mode='HTML')
            return
        return
    n_match = re.match('^[6-9]\\d{9}$', txt)
    u_match = re.match('^@[a-zA-Z0-9_.]{4,}$', txt) if txt.startswith('@') else None
    if not n_match and (not u_match):
        return
    if is_identifier_blocked(str(uid)):
        return
    if is_group_muted(cid):
        return
    grp_g = get_group(cid)
    if grp_g and safe_g(grp_g, 6) == 1:
        return
    user_g = get_user(uid)
    if not user_g:
        add_user(uid, uname, fname)
        user_g = get_user(uid)
    _grp_unl = grp_g and safe_g(grp_g, 5) == 1
    if not is_admin(uid) and (not _grp_unl):
        _ucr = get_credits(uid)
        try:
            _ucr_int = int(_ucr) if _ucr != '∞' else 999
        except:
            _ucr_int = 0
        if _ucr_int <= 0:
            _nocr_txt, _nocr_mk = no_credits_msg(uid)
            try:
                bot.reply_to(m, _nocr_txt, reply_markup=_nocr_mk, parse_mode='HTML')
            except:
                bot.send_message(cid, _nocr_txt, reply_markup=_nocr_mk, parse_mode='HTML')
            return
    if not deduct_credit(uid, 1, cid):
        return
    ld = bot.reply_to(m, '<blockquote>' + pbar(0) + '\n ꜰᴇᴛᴄʜɪɴɢ...</blockquote>', parse_mode='HTML')
    try:
        if n_match:
            num = txt
            if is_identifier_blocked(num):
                try:
                    bot.edit_message_text('<blockquote> Blocked.</blockquote>', cid, ld.message_id, parse_mode='HTML')
                except:
                    pass
                refund_credit(uid, 1)
                return
            _t0 = time.time()
            res = api_number(num)
            _elapsed = time.time() - _t0
            _send_number_result(cid, ld.message_id, res, num, uid, _elapsed, edit=True)
            if res and res.get('success'):
                c.execute('INSERT INTO search_history(user_id,search_type,query,search_date,result) VALUES(?,?,?,?,?)', (uid, 'number', num, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), json.dumps(res)))
                conn.commit()
                log_search(uid, fname, uname, 'NUMBER(GROUP)', num)
            else:
                refund_credit(uid, 1)
        elif u_match:
            un = txt
            if is_identifier_blocked(un.replace('@', '').lower()):
                try:
                    bot.edit_message_text('<blockquote> Blocked.</blockquote>', cid, ld.message_id, parse_mode='HTML')
                except:
                    pass
                refund_credit(uid, 1)
                return
            _un_clean = un.lstrip('@').lower()
            import concurrent.futures as _cfu_grp
            try:
                with _cfu_grp.ThreadPoolExecutor(max_workers=1) as _ex_grp:
                    _fut_grp = _ex_grp.submit(api_full_user, un)
                    res = _fut_grp.result(timeout=30)
            except Exception:
                res = None
            now = _now_ist()
            _cr_left_grp = get_credits(uid)
            rtxt, pic = _fmt_tg_user_short(res, un, now, _cr_left_grp)
            try:
                bot.edit_message_text(rtxt, cid, ld.message_id, parse_mode='HTML')
            except:
                bot.send_message(cid, rtxt, parse_mode='HTML')
            if res and res.get('success'):
                c.execute('INSERT INTO search_history(user_id,search_type,query,search_date,result) VALUES(?,?,?,?,?)', (uid, 'username', un, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), json.dumps(res)))
                conn.commit()
                log_search(uid, fname, uname, 'USERNAME(GROUP)', un, pic)
            else:
                refund_credit(uid, 1)
    except Exception as e:
        try:
            bot.edit_message_text(f'<blockquote>❌ Error: {_safe_err(e)}</blockquote>', cid, ld.message_id, parse_mode='HTML')
        except:
            pass

def do_search(uid, stype, query, m):
    _user_cache.pop(uid, None)
    user = get_user(uid)
    if not user:
        add_user(uid, m.from_user.username or '', m.from_user.first_name or 'User')
        user = get_user(uid)
    if not check_channel(uid):
        mk = get_channels_keyboard(uid)
        if mk:
            bot.reply_to(m, format_force_join_msg(), reply_markup=mk, parse_mode='HTML')
        user_state[uid] = S_NONE
        return
    if not is_admin(uid) and user[7] != 1 and (user[5] <= 0):
        txt, mk = no_credits_msg(uid)
        bot.reply_to(m, txt, reply_markup=mk, parse_mode='HTML')
        user_state[uid] = S_NONE
        return
    _cost = 1
    if not deduct_credit(uid, _cost):
        bot.reply_to(m, '<blockquote> No credits!\n @notCoder2006</blockquote>', parse_mode='HTML')
        user_state[uid] = S_NONE
        return
    sm = bot.reply_to(m, '<blockquote>' + pbar(0) + '\nꜱᴛᴀʀᴛɪɴɢ...</blockquote>', parse_mode='HTML')
    _stype_key_map = {S_NUM: 'number', S_USER: 'username', S_TID: 'tgid', S_ADH: 'aadhar', S_INSTA: 'instagram', S_FF: 'freefire', S_FFL: 'like', S_VEH: 'vehicle', S_BOMB: 'bomber'}
    try:
        bot.send_chat_action(m.chat.id, 'typing')
    except:
        pass
    stop_anim = _start_anim(m.chat.id, sm.message_id, _stype_key_map.get(stype, 'number'))
    res = None
    rtxt = None
    pic = None
    nm = m.from_user.first_name or 'User'
    extra_ff = None
    if stype == S_NUM:
        _t0 = time.time()
        res = api_number(query)
        _elapsed = time.time() - _t0
        rtxt, total_pages, _, has_next = fmt_number_page(res, query, 1, per_page=2, uid=uid, elapsed=_elapsed)
        _num_cache[uid] = {'data': res, 'num': query, 'page': 1, 'total': total_pages, 'elapsed': _elapsed}
    elif stype in (S_USER, S_TID):
        import concurrent.futures as _cfu_ds
        try:
            with _cfu_ds.ThreadPoolExecutor(max_workers=1) as _ex_ds:
                _fut_ds = _ex_ds.submit(api_full_user, query)
                res = _fut_ds.result(timeout=30)
        except Exception:
            res = None
        now = _now_ist()
        icon = '' if stype == S_USER else ''
        title_t = 'USERNAME INFO' if stype == S_USER else 'TG ID INFO'
        label = query if stype == S_USER else f'ID: {query}'
        _cr_left = get_credits(uid) if not is_admin(uid) else '∞'
        if stype == S_USER:
            rtxt, _ = _fmt_tg_user_short(res, label, now, _cr_left)
        else:
            rtxt, _ = _fmt_tg_user(res, icon, title_t, label, now, _cr_left)
        pic = None
    elif stype == S_ADH:
        res = api_aadhar(query)
        rtxt = fmt_aadhar(res, query, nm)
    elif stype == S_INSTA:
        res = api_instagram(query)
        rtxt, pic = fmt_instagram(res, query, nm)
    elif stype == S_FF:
        res = api_ff(query)
        p1ff, p2ff = fmt_ff(res, query, nm)
        rtxt = p1ff
        extra_ff = p2ff
    elif stype == S_FFL:
        import concurrent.futures as _cf
        with _cf.ThreadPoolExecutor(max_workers=2) as _ex:
            _f1 = _ex.submit(api_ff, query)
            _f2 = _ex.submit(api_ff_like, query)
            ff_info = _f1.result()
            res = _f2.result()
        lb = ff_info.get('liked', 0) if ff_info else 0
        rtxt = fmt_ff_like(res, query, nm, lb)
    elif stype == S_VEH:
        res = api_vehicle(query)
        rtxt = fmt_vehicle(res, query, nm)
    elif stype == S_BOMB:
        stop_anim[0] = True
        if bomber_jobs.get(uid, {}).get('running', False):
            try:
                bot.edit_message_text('<blockquote> Already running! STOP first.</blockquote>', uid, sm.message_id, parse_mode='HTML')
            except:
                pass
            user_state[uid] = S_NONE
            return
        threading.Thread(target=run_bomber, args=(uid, uid, query, sm.message_id), daemon=True).start()
        user_state[uid] = S_NONE
        return
    stop_anim[0] = True
    if rtxt and stype not in (S_USER, S_TID, S_NUM):
        try:
            _cr_now = get_credits(uid) if not is_admin(uid) else '∞'
            _te_cr = f"🪙"
            _cr_inject = f'\n{_te_cr} ᴄʀᴇᴅɪᴛꜱ ʟᴇꜰᴛ:- <b>{_cr_now}</b>'
            if rtxt.endswith('</blockquote>'):
                rtxt = rtxt[:-len('</blockquote>')] + _cr_inject + '</blockquote>'
        except:
            pass
    ok = res and (res.get('success') or res.get('blocked'))
    if not ok and (not is_admin(uid)) and (user[7] != 1):
        refund_credit(uid, _cost)
    if stype == S_NUM:
        if rtxt:
            cache = _num_cache.get(uid, {})
            total_pages = cache.get('total', 1)
            mk_pg = _num_page_markup(uid, 1, total_pages)
            try:
                bot.edit_message_text(rtxt, m.chat.id, sm.message_id, reply_markup=mk_pg, parse_mode='HTML')
            except:
                bot.send_message(m.chat.id, rtxt, reply_markup=mk_pg, parse_mode='HTML')
    elif stype in (S_USER, S_TID):
        if rtxt:
            try:
                bot.edit_message_text(rtxt, m.chat.id, sm.message_id, parse_mode='HTML')
            except:
                bot.send_message(m.chat.id, rtxt, parse_mode='HTML')
    elif rtxt:
        send_with_pfp(m.chat.id, rtxt, pic, sm.message_id)
    if ok and res:
        c.execute('INSERT INTO search_history(user_id,search_type,query,search_date,result) VALUES(?,?,?,?,?)', (uid, stype, query, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), json.dumps(res)))
        conn.commit()
        log_search(uid, m.from_user.first_name or 'User', m.from_user.username or '', stype, query, pic)
    if stype == S_FF and ok and extra_ff and isinstance(extra_ff, str) and extra_ff.startswith('http'):
        try:
            bot.send_photo(m.chat.id, extra_ff, caption=' <b>Profile Avatar</b>', parse_mode='HTML')
        except:
            pass
    elif stype == S_FF and ok and extra_ff:
        try:
            bot.send_message(m.chat.id, extra_ff, parse_mode='HTML')
        except:
            pass
    user_state[uid] = S_NONE

# ======================= CHANNEL / GROUP MENU (keyboard only, 2-level) =======================
# Admin Page 2 -> CHANNEL MENU -> [CHANNEL ADMIN] [GROUP ADMIN] [BACK]
#   CHANNEL ADMIN -> ADD CHANNEL (link -> channel id) / REMOVE CHANNEL / CHANNEL LIST / BACK
#   GROUP ADMIN   -> ADD GROUP (group id -> group link) / REMOVE GROUP / GROUP LIST / BACK
_FJ2_BACK = ' BACK TO ADMIN P2'
_fj2 = {}
_FJ2_LINK_RE = re.compile(r'https://t\.me/(\+[A-Za-z0-9_-]{6,}|joinchat/[A-Za-z0-9_-]{6,}|[A-Za-z][A-Za-z0-9_]{4,})')

def kb_ch_sub():
    mk = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    mk.row(_KB('➕ ADD CHANNEL', style='success'), _KB('🗑 REMOVE CHANNEL', style='danger'))
    mk.row(_KB('📋 CHANNEL LIST', style='primary'))
    mk.row(_KB(_FJ2_BACK, style='danger'))
    return mk

def kb_grp_sub():
    mk = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    mk.row(_KB('➕ ADD GROUP', style='success'), _KB('🗑 REMOVE GROUP', style='danger'))
    mk.row(_KB('📋 GROUP LIST', style='primary'))
    mk.row(_KB(_FJ2_BACK, style='danger'))
    return mk

def _fj2_sub_kb(kind):
    return kb_ch_sub() if kind == 'channel' else kb_grp_sub()

def _fj2_norm_link(raw):
    s = (raw or '').strip()
    if re.fullmatch(r'@[A-Za-z][A-Za-z0-9_]{4,}', s):
        s = 'https://t.me/' + s[1:]
    s = re.sub(r'^http://', 'https://', s, flags=re.I)
    s = re.sub(r'^https://telegram\.me/', 'https://t.me/', s, flags=re.I)
    s = re.sub(r'^https://t\.me/', 'https://t.me/', s, flags=re.I)
    s = s.rstrip('/')
    return s if _FJ2_LINK_RE.fullmatch(s) else None

def _fj2_vis(link):
    tail = link.split('t.me/', 1)[1]
    return 'private' if (tail.startswith('+') or tail.lower().startswith('joinchat/')) else 'public'

def _fj2_ask(chat_id, text, nxt):
    sent = bot.send_message(chat_id, text, parse_mode='HTML', reply_markup=kb_fj_cancel())
    bot.register_next_step_handler(sent, nxt)

def _fj2_fail(chat_id, kind, text):
    try:
        bot.send_message(chat_id, f'<blockquote>❌ {text}</blockquote>', parse_mode='HTML', reply_markup=_fj2_sub_kb(kind))
    except Exception as e:
        print(f'[FJ2_FAIL] {e}')

def _fj2_open_sub(m, kind):
    uid = m.from_user.id
    _fj2.pop(uid, None)
    try:
        bot.clear_step_handler_by_chat_id(m.chat.id)
    except Exception:
        pass
    user_state[uid] = 'ADMIN_CHANNEL_MGMT' if kind == 'channel' else 'ADMIN_GROUP_FJ_MGMT'
    title = 'Channel Admin' if kind == 'channel' else 'Group Admin'
    bot.send_message(m.chat.id, f'<blockquote> <b>{title}</b></blockquote>', reply_markup=_fj2_sub_kb(kind), parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text == '📢 CHANNEL ADMIN' and is_admin(m.from_user.id))
def h_fj2_open_channel(m):
    _fj2_open_sub(m, 'channel')

@bot.message_handler(func=lambda m: m.text == '👥 GROUP ADMIN' and is_admin(m.from_user.id))
def h_fj2_open_group(m):
    _fj2_open_sub(m, 'group')

# ---------- ADD CHANNEL: link -> channel id ----------
@bot.message_handler(func=lambda m: m.text == '➕ ADD CHANNEL' and is_admin(m.from_user.id))
def h_fj2_add_channel(m):
    uid = m.from_user.id
    _fj2[uid] = {'kind': 'channel'}
    _fj2_ask(m.chat.id, '<blockquote>➕ <b>ADD CHANNEL</b>\n\n🔗 Pehle channel ka <b>link</b> bhejo:\n<code>https://t.me/username</code>\nPrivate: <code>https://t.me/+xxxxxxxx</code></blockquote>', _fj2_ch_link)

def _fj2_ch_link(m):
    uid = m.from_user.id
    if not is_admin(uid):
        return
    st = _fj2.get(uid)
    if not st or st.get('kind') != 'channel':
        _fj2_fail(m.chat.id, 'channel', 'Session expired. ➕ ADD CHANNEL dobara dabao.'); return
    link = _fj2_norm_link(m.text)
    if not link:
        _fj2_ask(m.chat.id, '<blockquote>❌ Invalid link!\nFormat: <code>https://t.me/username</code> ya <code>https://t.me/+xxxxxxxx</code>\n\n🔗 Link dobara bhejo:</blockquote>', _fj2_ch_link); return
    st['url'] = link
    st['vis'] = _fj2_vis(link)
    _fj2_ask(m.chat.id, '<blockquote>🆔 Ab <b>Channel ID</b> bhejo:\n<code>-100xxxxxxxxxx</code></blockquote>', _fj2_ch_id)

def _fj2_ch_id(m):
    uid = m.from_user.id
    if not is_admin(uid):
        return
    st = _fj2.get(uid)
    if not st or st.get('kind') != 'channel' or 'url' not in st:
        _fj2_fail(m.chat.id, 'channel', 'Session expired. ➕ ADD CHANNEL dobara dabao.'); return
    raw = (m.text or '').strip()
    if not re.fullmatch(r'-100\d{5,}', raw):
        _fj2_ask(m.chat.id, '<blockquote>❌ Invalid Channel ID!\nFormat: <code>-100xxxxxxxxxx</code>\n\n🆔 Channel ID dobara bhejo:</blockquote>', _fj2_ch_id); return
    _fj2_verify_and_save(m, st, raw, ('channel',), 'Ye ID channel ki nahi hai.')

# ---------- ADD GROUP: group id -> group link ----------
@bot.message_handler(func=lambda m: m.text == '➕ ADD GROUP' and is_admin(m.from_user.id))
def h_fj2_add_group(m):
    uid = m.from_user.id
    _fj2[uid] = {'kind': 'group'}
    _fj2_ask(m.chat.id, '<blockquote>➕ <b>ADD GROUP</b>\n\n🆔 Pehle <b>Group ID</b> bhejo:\n<code>-100xxxxxxxxxx</code></blockquote>', _fj2_grp_id)

def _fj2_grp_id(m):
    uid = m.from_user.id
    if not is_admin(uid):
        return
    st = _fj2.get(uid)
    if not st or st.get('kind') != 'group':
        _fj2_fail(m.chat.id, 'group', 'Session expired. ➕ ADD GROUP dobara dabao.'); return
    raw = (m.text or '').strip()
    if not re.fullmatch(r'-\d{5,}', raw):
        _fj2_ask(m.chat.id, '<blockquote>❌ Invalid Group ID!\nFormat: <code>-100xxxxxxxxxx</code>\n\n🆔 Group ID dobara bhejo:</blockquote>', _fj2_grp_id); return
    info = _fj2_check_chat(m.chat.id, 'group', raw, ('group', 'supergroup'), 'Ye ID group ki nahi hai.')
    if not info:
        return
    st.update(info)
    _fj2_ask(m.chat.id, '<blockquote>🔗 Ab <b>Group Link</b> bhejo:\n<code>https://t.me/username</code>\nPrivate: <code>https://t.me/+xxxxxxxx</code></blockquote>', _fj2_grp_link)

def _fj2_grp_link(m):
    uid = m.from_user.id
    if not is_admin(uid):
        return
    st = _fj2.get(uid)
    if not st or st.get('kind') != 'group' or 'chat_id' not in st:
        _fj2_fail(m.chat.id, 'group', 'Session expired. ➕ ADD GROUP dobara dabao.'); return
    link = _fj2_norm_link(m.text)
    if not link:
        _fj2_ask(m.chat.id, '<blockquote>❌ Invalid link!\nFormat: <code>https://t.me/username</code> ya <code>https://t.me/+xxxxxxxx</code>\n\n🔗 Link dobara bhejo:</blockquote>', _fj2_grp_link); return
    st['url'] = link
    st['vis'] = _fj2_vis(link)
    if not _fj2_link_matches(m.chat.id, st):
        return
    _fj2_save(m.chat.id, uid, st)

# ---------- shared helpers ----------
def _fj2_check_chat(chat_id, kind, raw, types, wrong_type_msg):
    """Chat fetch + type check + bot-is-admin check. Returns dict or None (error already sent)."""
    try:
        ch = bot.get_chat(int(raw))
    except Exception as e:
        _fj2_fail(chat_id, kind, f'Chat nahi mila ya bot us chat mein nahi hai.\n<code>{_html.escape(_safe_err(e))}</code>'); return None
    if getattr(ch, 'type', '') not in types:
        _fj2_fail(chat_id, kind, wrong_type_msg); return None
    try:
        me = bot.get_me()
        mem = bot.get_chat_member(ch.id, me.id)
        if getattr(mem, 'status', '') not in ('administrator', 'creator'):
            raise ValueError('not admin')
    except Exception:
        _fj2_fail(chat_id, kind, 'Bot ko is chat mein <b>Admin</b> banao, phir dobara add karo.'); return None
    return {'chat_id': str(ch.id), 'title': ch.title or str(ch.id), 'username': getattr(ch, 'username', None)}

def _fj2_link_matches(chat_id, st):
    """Public link ka username chat ke username se match hona chahiye."""
    if st.get('vis') == 'public':
        un = st.get('username')
        tail = st['url'].split('t.me/', 1)[1]
        if not un:
            _fj2_fail(chat_id, st['kind'], 'Is chat ka public @username nahi hai. Private invite link do (<code>https://t.me/+xxxx</code>).'); return False
        if un.lower() != tail.lower():
            _fj2_fail(chat_id, st['kind'], 'Link aur ID match nahi karte. Sahi link/ID se dobara add karo.'); return False
    return True

def _fj2_verify_and_save(m, st, raw, types, wrong_type_msg):
    info = _fj2_check_chat(m.chat.id, st['kind'], raw, types, wrong_type_msg)
    if not info:
        return
    st.update(info)
    if not _fj2_link_matches(m.chat.id, st):
        return
    _fj2_save(m.chat.id, m.from_user.id, st)

def _fj2_save(chat_id, uid, st):
    kind = st['kind']
    try:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        row = c.execute('SELECT id FROM force_join_channels WHERE chat_id=?', (st['chat_id'],)).fetchone()
        if row:
            c.execute('UPDATE force_join_channels SET chat_title=?,chat_url=?,added_by=?,added_date=?,is_active=1,chat_type=?,visibility=? WHERE id=?',
                      (st['title'], st['url'], uid, now, kind, st['vis'], row[0]))
        else:
            c.execute('INSERT INTO force_join_channels(chat_id,chat_title,chat_url,added_by,added_date,is_active,chat_type,visibility) VALUES(?,?,?,?,?,1,?,?)',
                      (st['chat_id'], st['title'], st['url'], uid, now, kind, st['vis']))
        conn.commit()
        _channel_check_cache.clear()
        _fj2.pop(uid, None)
        bot.send_message(chat_id, f"<blockquote>✅ <b>{kind.upper()} added</b> ({st['vis'].upper()})\n📢 {_html.escape(st['title'])}\n🆔 <code>{st['chat_id']}</code>\n🔗 {_html.escape(st['url'])}\n\n🔒 Force Join: <b>ON</b></blockquote>", parse_mode='HTML', reply_markup=_fj2_sub_kb(kind))
    except Exception as e:
        _fj2_fail(chat_id, kind, f'Database error: {_html.escape(_safe_err(e))}')

def _fj2_targets(kind):
    """Active targets of one kind: list of (chat_id, title, url, visibility, is_default)."""
    out, seen = [], set()
    if kind == 'channel':
        for cid, title, url in FORCE_JOIN_DEFAULT_CHANNELS:
            out.append((cid, title, url, 'public', True)); seen.add(_fj_normalize(cid))
    try:
        rows = c.execute("SELECT chat_id,chat_title,chat_url,COALESCE(chat_type,'channel'),COALESCE(visibility,'public') FROM force_join_channels WHERE is_active=1 ORDER BY id").fetchall()
    except Exception:
        rows = []
    for r in rows:
        if r[3] != kind:
            continue
        nk = _fj_normalize(r[0])
        if nk in seen:
            continue
        seen.add(nk)
        out.append((r[0], r[1], r[2], r[4], False))
    return out

def _fj2_send_list(m, kind):
    items = _fj2_targets(kind)
    word = kind.upper()
    if not items:
        bot.send_message(m.chat.id, f'<blockquote>Koi {kind} nahi hai abhi.\n\n➕ ADD {word} se add karo.</blockquote>', parse_mode='HTML', reply_markup=_fj2_sub_kb(kind)); return
    parts = []
    for i, (cid, title, url, vis, _d) in enumerate(items, 1):
        parts.append(f'{i}. <b>{_html.escape(str(title))}</b> [{str(vis).upper()}]\n🆔 <code>{_html.escape(str(cid))}</code>\n🔗 {_html.escape(str(url or ""))}')
    head = f'📋 <b>{word} LIST</b>\n' + '─' * 22 + '\n\n'
    foot = '\n' + '─' * 22 + f'\nTotal: {len(items)}'
    chunks, cur = [], ''
    for p in parts:
        if len(cur) + len(p) > 3200:
            chunks.append(cur); cur = ''
        cur += p + '\n\n'
    if cur:
        chunks.append(cur)
    for idx, ch_txt in enumerate(chunks):
        txt = '<blockquote>' + (head if idx == 0 else '') + ch_txt.rstrip('\n') + (foot if idx == len(chunks) - 1 else '') + '</blockquote>'
        bot.send_message(m.chat.id, txt, parse_mode='HTML', reply_markup=_fj2_sub_kb(kind) if idx == len(chunks) - 1 else None)

@bot.message_handler(func=lambda m: m.text == '📋 CHANNEL LIST' and is_admin(m.from_user.id))
def h_fj2_list_channel(m):
    _fj2_send_list(m, 'channel')

@bot.message_handler(func=lambda m: m.text == '📋 GROUP LIST' and is_admin(m.from_user.id))
def h_fj2_list_group(m):
    _fj2_send_list(m, 'group')

# ---------- REMOVE: har target ek keyboard button ----------
def _fj2_send_remove(m, kind):
    uid = m.from_user.id
    _fj2.pop(uid, None)
    try:
        bot.clear_step_handler_by_chat_id(m.chat.id)
    except Exception:
        pass
    items = [t for t in _fj2_targets(kind) if not t[4]]
    word = kind.upper()
    if not items:
        bot.send_message(m.chat.id, f'<blockquote>Koi removable {kind} nahi hai.\n\n➕ ADD {word} se add karo.</blockquote>', parse_mode='HTML', reply_markup=_fj2_sub_kb(kind)); return
    mk = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    for cid, title, url, vis, _d in items[:90]:
        t = re.sub(r'\s+', ' ', str(title or kind)).replace(' | ', ' ').strip()[:28]
        mk.row(_KB(f'🗑 {t} | {cid}', style='danger'))
    mk.row(_KB(_FJ2_BACK, style='danger'))
    bot.send_message(m.chat.id, f'<blockquote>🗑 <b>REMOVE {word}</b>\n\nJise remove karna hai uska button dabao 👇\nTotal: {len(items)}</blockquote>', parse_mode='HTML', reply_markup=mk)

@bot.message_handler(func=lambda m: m.text == '🗑 REMOVE CHANNEL' and is_admin(m.from_user.id))
def h_fj2_rem_channel(m):
    _fj2_send_remove(m, 'channel')

@bot.message_handler(func=lambda m: m.text == '🗑 REMOVE GROUP' and is_admin(m.from_user.id))
def h_fj2_rem_group(m):
    _fj2_send_remove(m, 'group')

@bot.message_handler(func=lambda m: bool(m.text) and m.text.startswith('🗑 ') and ' | ' in m.text and is_admin(m.from_user.id))
def h_fj2_do_remove(m):
    cid = m.text.rsplit(' | ', 1)[1].strip()
    try:
        if _fj_normalize(cid) in {_fj_normalize(x[0]) for x in FORCE_JOIN_DEFAULT_CHANNELS}:
            bot.send_message(m.chat.id, '<blockquote>⚠️ Default force-join channel remove nahi ho sakta.</blockquote>', parse_mode='HTML', reply_markup=kb_ch_sub()); return
        row = c.execute("SELECT id,chat_title,COALESCE(chat_type,'channel') FROM force_join_channels WHERE chat_id=? AND is_active=1", (cid,)).fetchone()
        if not row:
            bot.send_message(m.chat.id, '<blockquote>❌ Ye target ab active nahi hai.</blockquote>', parse_mode='HTML', reply_markup=kb_ch_sub()); return
        c.execute('UPDATE force_join_channels SET is_active=0 WHERE id=?', (row[0],))
        conn.commit()
        _channel_check_cache.clear()
        kind = row[2] if row[2] in ('channel', 'group') else 'channel'
        bot.send_message(m.chat.id, f'<blockquote>✅ <b>{kind.upper()} removed</b>\n📢 {_html.escape(str(row[1]))}\n🆔 <code>{_html.escape(cid)}</code></blockquote>', parse_mode='HTML', reply_markup=_fj2_sub_kb(kind))
    except Exception as e:
        bot.send_message(m.chat.id, f'<blockquote>❌ Database error: {_html.escape(_safe_err(e))}</blockquote>', parse_mode='HTML', reply_markup=kb_ch_sub())


# ---------------- menu-button interrupt for "send ID" prompts ----------------
def _kb_texts(mk):
    out = set()
    try:
        rows = getattr(mk, 'keyboard', None)
        if rows is None and hasattr(mk, 'buttons'):
            rows = [mk.buttons()]
        for r in rows or []:
            for b in (r if isinstance(r, (list, tuple)) else [r]):
                t = b.get('text') if isinstance(b, dict) else getattr(b, 'text', None)
                if t:
                    out.add(t)
    except Exception:
        pass
    return out

def _menu_texts():
    out = set()
    for f in (kb_admin_p1, kb_admin_p2, kb_admin_mgmt, kb_channel_mgmt, kb_ch_sub, kb_grp_sub, kb_fj_type, kb_fj_vis, kb_fj_cancel):
        try:
            out |= _kb_texts(f())
        except Exception:
            pass
    out |= {'ᴀᴅᴍɪɴ ᴩᴀɴᴇʟ', 'ᴍᴀɪɴ ᴍᴇɴᴜ'}
    return out

def _interruptible(fn):
    def w(m):
        try:
            t = m.text or ''
            if t.strip().startswith('/') or t in _menu_texts() or t.strip() in _menu_texts():
                if t != '❌ CANCEL':
                    _fj_add_state.pop(m.from_user.id, None)
                bot.process_new_messages([m])
                return
        except Exception as e:
            print(f'[INTERRUPT] {e}')
        return fn(m)
    w.__name__ = getattr(fn, '__name__', 'w')
    return w

for _n in ('do_addadm', 'do_remadm', 'do_quick_ban', 'do_ublku', 'do_remch', '_fj_add_chatid', '_fj_add_link', '_fj2_ch_link', '_fj2_ch_id', '_fj2_grp_id', '_fj2_grp_link'):
    if _n in globals():
        globals()[_n] = _interruptible(globals()[_n])


@bot.message_handler(func=lambda m: m.text and (not m.text.startswith('/')) and (m.chat.type == 'private'))
def h_private(m):
    uid = m.from_user.id
    txt = m.text.strip()
    st = user_state.get(uid, S_NONE)
    try:
        if is_maintenance() and (not is_admin(uid)):
            _mm = _get_setting('maintenance_msg', ' <b>Bot under maintenance</b>\nThodi der baad try karo.')
            bot.reply_to(m, f'<blockquote>{_mm}\n⚡ @notCoder2006</blockquote>', parse_mode='HTML')
            return
    except:
        pass
    if check_blocked_and_reply(uid):
        return
    if st == S_NONE:
        if re.match('^[6-9]\\d{9}$', txt) and is_feature_enabled('number'):
            user = get_user(uid)
            if not user:
                add_user(uid, m.from_user.username or '', m.from_user.first_name or 'User')
            do_search(uid, S_NUM, txt, m)
            return
        if re.match('^@[a-zA-Z0-9_.]{5,}$', txt) and is_feature_enabled('username'):
            user = get_user(uid)
            if not user:
                add_user(uid, m.from_user.username or '', m.from_user.first_name or 'User')
            do_search(uid, S_USER, txt, m)
            return
    if st == S_NUM:
        if re.match('^[6-9]\\d{9}$', txt):
            do_search(uid, S_NUM, txt, m)
        else:
            bot.reply_to(m, '<blockquote> Invalid! 10-digit number</blockquote>', parse_mode='HTML')
    elif st == S_USER:
        if txt.startswith('@') and len(txt) > 1:
            do_search(uid, S_USER, txt, m)
        elif re.sub('\\D', '', txt) and len(re.sub('\\D', '', txt)) >= 5:
            do_search(uid, S_TID, re.sub('\\D', '', txt), m)
        else:
            bot.reply_to(m, '<blockquote> @username ya numeric TG ID bhejo!</blockquote>', parse_mode='HTML')
    elif st == S_TID:
        cl = re.sub('\\D', '', txt)
        if len(cl) >= 5:
            do_search(uid, S_TID, cl, m)
        else:
            bot.reply_to(m, '<blockquote> Invalid User ID!</blockquote>', parse_mode='HTML')
    elif st == S_ADH:
        cl = re.sub('\\D', '', txt)
        if len(cl) == 12:
            do_search(uid, S_ADH, cl, m)
        else:
            bot.reply_to(m, '<blockquote> Invalid! 12-digit Aadhar</blockquote>', parse_mode='HTML')
    elif st == S_INSTA:
        cl = txt.replace('@', '').strip()
        if re.match('^[a-zA-Z0-9_.]{1,30}$', cl):
            do_search(uid, S_INSTA, cl, m)
        else:
            bot.reply_to(m, '<blockquote> Invalid Instagram!</blockquote>', parse_mode='HTML')
    elif st == S_FF:
        cl = re.sub('\\D', '', txt)
        if len(cl) >= 5:
            do_search(uid, S_FF, cl, m)
        else:
            bot.reply_to(m, '<blockquote> Invalid FF UID!</blockquote>', parse_mode='HTML')
    elif st == S_FFL or st == S_FF_LIKE_UID:
        cl = re.sub('\\D', '', txt)
        if len(cl) >= 5:
            user_state[uid] = S_NONE
            if not _like_check_ratelimit(uid) and (not is_admin(uid)):
                bot.reply_to(m, f'<blockquote>⚠️ Daily limit reached! Max {LIKE_DAILY_MAX}/day\n⚡ @notCoder2006</blockquote>', parse_mode='HTML')
                return
            can, rem, cinfo = _like_check_cooldown(uid, cl)
            if not can and (not is_admin(uid)):
                h = int(rem // 3600)
                mn = int(rem % 3600 // 60)
                bot.reply_to(m, f'<blockquote>{_F}\n⏰ <b>UID ON COOLDOWN</b>\n{_F}\n\n❌ This UID is on cooldown!\n\n🆔 UID: <code>{cl}</code>\n⏱️ Remaining: {h}h {mn}m\n\n💡 Different UID like karo — no cooldown!\n\n{_F}\n⚡ @notCoder2006\n{_F}</blockquote>', parse_mode='HTML')
                return
            sm = bot.reply_to(m, '<blockquote>' + pbar(0) + '\nꜱᴛᴀʀᴛɪɴɢ...</blockquote>', parse_mode='HTML')
            try:
                bot.send_chat_action(m.chat.id, 'typing')
            except:
                pass
            threading.Thread(target=do_ff_like_send, args=(uid, sm.message_id, cl, 'ind', uid, m.from_user.first_name or 'User'), daemon=True).start()
        else:
            bot.reply_to(m, '<blockquote> Invalid FF UID!</blockquote>', parse_mode='HTML')
    elif st == S_VEH:
        cl = txt.upper().replace(' ', '')
        if re.match('^[A-Z]{2}[0-9]{1,2}[A-Z]{1,3}[0-9]{4}$', cl):
            do_search(uid, S_VEH, cl, m)
        else:
            bot.reply_to(m, '<blockquote> Invalid RC! Example: MH12AB1234</blockquote>', parse_mode='HTML')
    elif st == S_BOMB:
        n = re.sub('\\D', '', txt)
        if len(n) == 12 and n.startswith('91'):
            n = n[2:]
        if re.match('^[6-9]\\d{9}$', n):
            do_search(uid, S_BOMB, n, m)
        else:
            bot.reply_to(m, '<blockquote> Invalid number!\n Sirf apne number!</blockquote>', parse_mode='HTML')
    elif st == S_REDEEM:
        ok, msg = redeem_code_fn(uid, txt)
        bot.send_message(uid, f'<blockquote>{msg}\n⚡ @notCoder2006</blockquote>', parse_mode='HTML')
        user_state[uid] = S_NONE
    elif st == S_PREM_REDEEM:
        ok, pmsg = redeem_premium_code_fn(uid, txt)
        bot.send_message(uid, f'<blockquote>{pmsg}\n⚡ @notCoder2006</blockquote>', parse_mode='HTML')
        user_state[uid] = S_NONE
@bot.message_handler(commands=['resetgroupcredits'])
def cmd_reset_group_credits(msg):
    """Sabhi groups ki credits 0 karo — sirf owner. Ab sirf user personal credits kaam karengi."""
    uid = msg.from_user.id
    if uid != OWNER_ID:
        bot.reply_to(msg, '<blockquote> Sirf owner use kar sakta hai!</blockquote>', parse_mode='HTML')
        return
    try:
        c.execute('UPDATE groups SET credits=0, unlimited=0')
        conn.commit()
        _group_cache.clear()
        count = c.execute('SELECT COUNT(*) FROM groups').fetchone()[0]
        bot.reply_to(msg, f'<blockquote>✅ <b>Group Credits Reset Done!</b>\n\n🔢 Total Groups: <code>{count}</code>\n💰 All Group Credits → <b>0</b>\n∞ Unlimited → <b>OFF</b>\n\nAb sirf user ke personal credits kaam karenge.\n⚡ @notCoder2006</blockquote>', parse_mode='HTML')
    except Exception as e:
        bot.reply_to(msg, f'<blockquote>❌ Error: {_safe_err(e)}</blockquote>', parse_mode='HTML')

@bot.message_handler(commands=['add'])
def cmd_add_credits(msg):
    """/add <amount> — reply pe user ko credits do (sirf owner/admin)"""
    uid = msg.from_user.id
    if not is_admin(uid):
        bot.reply_to(msg, '<blockquote> Sirf admin use kar sakta hai!\n @notCoder2006</blockquote>', parse_mode='HTML')
        return
    if not msg.reply_to_message:
        bot.reply_to(msg, '<blockquote> <b>Usage:</b>\nKisi user ke message ko reply karke:\n<code>/add 50</code>\n\nUsse 50 credits mil jayenge!\n @notCoder2006</blockquote>', parse_mode='HTML')
        return
    parts = msg.text.strip().split()
    if len(parts) < 2 or not parts[1].lstrip('-').isdigit():
        bot.reply_to(msg, '<blockquote> Format: <code>/add 50</code>\n @notCoder2006</blockquote>', parse_mode='HTML')
        return
    amount = int(parts[1])
    if amount == 0:
        bot.reply_to(msg, '<blockquote> Amount 0 nahi ho sakta!\n @notCoder2006</blockquote>', parse_mode='HTML')
        return
    target = msg.reply_to_message.from_user
    tid = target.id
    tfname = _html.escape(target.first_name or 'User')
    tuname = target.username or ''
    if not get_user(tid):
        add_user(tid, tuname, tfname)
    c.execute('UPDATE users SET credits=credits+? WHERE user_id=?', (amount, tid))
    conn.commit()
    _user_cache.pop(tid, None)
    new_cr = get_credits(tid)

    def _te(*args, **kwargs): return ""
    _L = _te('5465629669829128119') * 10
    _SM = _te('6147464060305676048')
    _CK = _te('6147565374289220368')
    _COIN = _te('5379600444098093058')
    _PLUS = _te('6179105681375760937')
    action = ' ᴀᴅᴅᴇᴅ' if amount > 0 else ' ʀᴇᴍᴏᴠᴇᴅ'
    bot.reply_to(msg, f"<blockquote>{_L}\n{_PLUS} <b>ᴄʀᴇᴅɪᴛꜱ ᴜᴘᴅᴀᴛᴇᴅ!</b>\n{_L}\n\n{_te('5373012449597335010')} ᴜꜱᴇʀ: <a href='tg://user?id={tid}'><b>{tfname}</b></a>\n{_te('5888781182249738113')} ɪᴅ: <code>{tid}</code>\n\n{_COIN} {action}: <b>{abs(amount)}</b>\n{_COIN} ɴᴇᴡ ᴛᴏᴛᴀʟ: <b>{new_cr}</b>\n\n{_L}\n{_SM} @notCoder2006 {_CK}\n{_L}</blockquote>", parse_mode='HTML')
    try:
        bot.send_message(tid, f'<blockquote>{_L}\n{_PLUS} <b>ᴄʀᴇᴅɪᴛꜱ ᴍɪʟᴇ!</b>\n{_L}\n\n{_COIN} +<b>{abs(amount)}</b> credits add ho gaye!\n{_COIN} ᴛᴏᴛᴀʟ: <b>{new_cr}</b>\n\n{_L}\n{_SM} @notCoder2006 {_CK}\n{_L}</blockquote>', parse_mode='HTML')
    except:
        pass
    try:
        try:
            bn = _get_bot_username()
        except:
            bn = '𝙽𝚘𝚝 𝙲𝚘𝚍𝚎𝚛_bot'
        log_token_activity(tid, tfname, tuname, amount, new_cr if isinstance(new_cr, int) else 0, f'Admin /add by {uid}', bn)
    except:
        pass

@bot.message_handler(commands=['spin'])
def cmd_spin(msg):
    """/spin - Daily spin — group + private dono mein kaam karta hai"""
    uid = msg.from_user.id
    fname = _html.escape(msg.from_user.first_name or 'User')
    uname = msg.from_user.username or ''
    cid = msg.chat.id
    chat_type = msg.chat.type
    if check_blocked_and_reply(uid):
        return
    user = get_user(uid)
    if not user:
        add_user(uid, uname, fname)
    if not check_channel(uid):
        mk_fj = get_channels_keyboard(uid)
        if mk_fj:
            bot.reply_to(msg, format_force_join_msg(), reply_markup=mk_fj, parse_mode='HTML')
            return
    if chat_type in ['group', 'supergroup']:
        threading.Thread(target=_do_group_spin, args=(uid, fname, uname, cid), daemon=True).start()
    elif is_admin(uid) or can_claim_daily(uid):
        dm = bot.send_dice(uid, emoji=_get_spin_emoji())
        time.sleep(5)
        cw = {1: 1, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5}.get(dm.dice.value, 1)
        c.execute('UPDATE users SET credits=credits+? WHERE user_id=?', (cw, uid))
        if not is_admin(uid):
            c.execute('INSERT OR IGNORE INTO daily_claims VALUES(?,?)', (uid, datetime.now().strftime('%Y-%m-%d')))
        conn.commit()
        _user_cache.pop(uid, None)
        user_obj = get_user(uid)
        tot = user_obj[5] if user_obj else cw
        _SS = _SEP()
        _SE = _SEP()
        _spin_ref = f'https://t.me/{_get_bot_username()}?start={uid}'
        _spin_vp_url = _spin_ref
        _spin_mk = InlineKeyboardMarkup()
        _spin_mk.add(_IKB(' Get More +5 Credits', style='success', url=_spin_vp_url))
        bot.send_message(uid, f'<blockquote>{_SS}\n🎁 <b>ᴅᴀɪʟʏ ꜱᴘɪɴ</b>\n{_SS}\n🎉 Won: <code>+{cw}</code> credits!\n💰 Total: <code>{tot}</code>\n{_SE}\n💰 ᴄʀᴇᴅɪᴛꜱ ʟᴇꜰᴛ: <b>{tot}</b>\n⚡ @notCoder2006</blockquote>', reply_markup=_spin_mk, parse_mode='HTML')
        try:
            bn = _get_bot_username()
        except:
            bn = '𝙽𝚘𝚝 𝙲𝚘𝚍𝚎𝚛_bot'
        log_token_activity(uid, fname, uname, cw, tot, 'Daily Spin', bn)
    else:
        bot.reply_to(msg, '<blockquote> <b>Already claimed today!</b>\n Kal wapis aao!\n @notCoder2006</blockquote>', parse_mode='HTML')

@bot.message_handler(commands=['wel', 'welcomeon', 'weloff', 'welcomeoff', 'onwelcome', 'offwelcome'])
def cmd_wel_toggle(msg):
    if msg.chat.type not in ['group', 'supergroup']:
        bot.reply_to(msg, '<blockquote> Ye command sirf group mein kaam karta hai!\n @notCoder2006</blockquote>', parse_mode='HTML')
        return
    uid = msg.from_user.id
    try:
        cm = bot.get_chat_member(msg.chat.id, uid)
        if cm.status not in ['administrator', 'creator'] and (not is_admin(uid)):
            bot.reply_to(msg, '<blockquote> Sirf group admin ya bot owner use kar sakta hai!\n @notCoder2006</blockquote>', parse_mode='HTML')
            return
    except:
        return
    cmd = msg.text.split()[0].lower().lstrip('/')
    parts = msg.text.strip().split()
    arg = parts[1].lower() if len(parts) > 1 else ''
    _wel_L = '' * 10
    _wel_CK = ''
    _wel_SM = ''
    _wel_BELL = ''
    _wel_MUTE = ''
    try:
        if cmd in ('weloff', 'welcomeoff', 'offwelcome') or arg == 'off':
            set_group_welcome_on(msg.chat.id, 0)
            bot.reply_to(msg, f'<blockquote>{_wel_L}\n{_wel_MUTE} <b>Welcome OFF</b>\n{_wel_L}\n\n❌ Ab naye members ka welcome message nahi aayega.\n\n💡 ON karne ke liye: <code>/onwelcome</code>\n\n{_wel_L}\n{_wel_SM} @notCoder2006 {_wel_CK}\n{_wel_L}</blockquote>', parse_mode='HTML')
        elif cmd in ('welcomeon', 'onwelcome') or arg == 'on':
            set_group_welcome_on(msg.chat.id, 1)
            bot.reply_to(msg, f'<blockquote>{_wel_L}\n{_wel_BELL} <b>Welcome ON</b>\n{_wel_L}\n\n✅ Ab naye members ka welcome message aayega! 🎉\n\n💡 OFF karne ke liye: <code>/offwelcome</code>\n\n{_wel_L}\n{_wel_SM} @notCoder2006 {_wel_CK}\n{_wel_L}</blockquote>', parse_mode='HTML')
        else:
            _cur_state = c.execute('SELECT welcome_on FROM group_welcome_settings WHERE group_id=?', (msg.chat.id,)).fetchone()
            _is_on = _cur_state[0] if _cur_state else 1
            _status_txt = f'{_wel_BELL} <b>Welcome abhi ON hai</b>' if _is_on else f'{_wel_MUTE} <b>Welcome abhi OFF hai</b>'
            bot.reply_to(msg, f'<blockquote>{_wel_L}\n{_status_txt}\n{_wel_L}\n\n💡 ON: <code>/wel on</code>\n💡 OFF: <code>/wel off</code>\n\n{_wel_L}\n{_wel_SM} @notCoder2006 {_wel_CK}\n{_wel_L}</blockquote>', parse_mode='HTML')
    except Exception as _we:
        print(f'[WEL_TOGGLE] {_we}')
        try:
            bot.reply_to(msg, '<blockquote> Error: Welcome toggle fail hua. Bot ko group admin banao!\n @notCoder2006</blockquote>', parse_mode='HTML')
        except:
            pass

@bot.message_handler(commands=['stopwelcome'])
def cmd_stop_welcome(msg):
    """Owner + group admin: /stopwelcome — welcome band karo"""
    if msg.chat.type not in ['group', 'supergroup']:
        bot.reply_to(msg, '<blockquote> Ye command sirf group mein kaam karta hai!\n @notCoder2006</blockquote>', parse_mode='HTML')
        return
    uid = msg.from_user.id
    try:
        cm = bot.get_chat_member(msg.chat.id, uid)
        if cm.status not in ['administrator', 'creator'] and (not is_admin(uid)):
            bot.reply_to(msg, '<blockquote> Sirf group admin ya bot owner use kar sakta hai!\n @notCoder2006</blockquote>', parse_mode='HTML')
            return
    except:
        return
    set_group_welcome_on(msg.chat.id, 0)
    _sw_L = '' * 10
    _sw_CK = ''
    _sw_SM = ''
    _sw_MUTE = ''
    bot.reply_to(msg, f'<blockquote>{_sw_L}\n{_sw_MUTE} <b>Welcome OFF</b>\n{_sw_L}\n\n❌ Ab naye members ka welcome message nahi aayega.\n\n💡 Dobara ON karne ke liye:\n<code>/startwelcome</code>\n\n{_sw_L}\n{_sw_SM} @notCoder2006 {_sw_CK}\n{_sw_L}</blockquote>', parse_mode='HTML')

@bot.message_handler(commands=['startwelcome'])
def cmd_start_welcome(msg):
    """Owner + group admin: /startwelcome — welcome ON karo"""
    if msg.chat.type not in ['group', 'supergroup']:
        bot.reply_to(msg, '<blockquote> Ye command sirf group mein kaam karta hai!\n @notCoder2006</blockquote>', parse_mode='HTML')
        return
    uid = msg.from_user.id
    try:
        cm = bot.get_chat_member(msg.chat.id, uid)
        if cm.status not in ['administrator', 'creator'] and (not is_admin(uid)):
            bot.reply_to(msg, '<blockquote> Sirf group admin ya bot owner use kar sakta hai!\n @notCoder2006</blockquote>', parse_mode='HTML')
            return
    except:
        return
    set_group_welcome_on(msg.chat.id, 1)
    _stw_L = '' * 10
    _stw_CK = ''
    _stw_SM = ''
    _stw_BELL = ''
    bot.reply_to(msg, f'<blockquote>{_stw_L}\n{_stw_BELL} <b>Welcome ON</b>\n{_stw_L}\n\n✅ Ab naye members ka welcome message aayega! 🎉\n\n💡 Band karne ke liye:\n<code>/stopwelcome</code>\n\n{_stw_L}\n{_stw_SM} @notCoder2006 {_stw_CK}\n{_stw_L}</blockquote>', parse_mode='HTML')

@bot.message_handler(commands=['offbye'])
def cmd_off_bye(msg):
    """Owner + group admin: /offbye — goodbye msg OFF karo"""
    if msg.chat.type not in ['group', 'supergroup']:
        bot.reply_to(msg, '<blockquote> Ye command sirf group mein kaam karta hai!\n @notCoder2006</blockquote>', parse_mode='HTML')
        return
    uid = msg.from_user.id
    try:
        cm = bot.get_chat_member(msg.chat.id, uid)
        if cm.status not in ['administrator', 'creator'] and (not is_admin(uid)):
            bot.reply_to(msg, '<blockquote> Sirf group admin ya bot owner use kar sakta hai!\n @notCoder2006</blockquote>', parse_mode='HTML')
            return
    except:
        return
    set_group_bye_on(msg.chat.id, 0)
    _ob_L = '' * 10
    _ob_CK = ''
    _ob_SM = ''
    _ob_MUTE = ''
    bot.reply_to(msg, f'<blockquote>{_ob_L}\n{_ob_MUTE} <b>Goodbye OFF</b>\n{_ob_L}\n\n❌ Ab group se jane wale members ka goodbye message nahi aayega.\n\n💡 Dobara ON karne ke liye:\n<code>/onbye</code>\n\n{_ob_L}\n{_ob_SM} @notCoder2006 {_ob_CK}\n{_ob_L}</blockquote>', parse_mode='HTML')

@bot.message_handler(commands=['onbye'])
def cmd_on_bye(msg):
    """Owner + group admin: /onbye — goodbye msg ON karo"""
    if msg.chat.type not in ['group', 'supergroup']:
        bot.reply_to(msg, '<blockquote> Ye command sirf group mein kaam karta hai!\n @notCoder2006</blockquote>', parse_mode='HTML')
        return
    uid = msg.from_user.id
    try:
        cm = bot.get_chat_member(msg.chat.id, uid)
        if cm.status not in ['administrator', 'creator'] and (not is_admin(uid)):
            bot.reply_to(msg, '<blockquote> Sirf group admin ya bot owner use kar sakta hai!\n @notCoder2006</blockquote>', parse_mode='HTML')
            return
    except:
        return
    set_group_bye_on(msg.chat.id, 1)
    _nb_L = '' * 10
    _nb_CK = ''
    _nb_SM = ''
    _nb_BELL = ''
    bot.reply_to(msg, f'<blockquote>{_nb_L}\n{_nb_BELL} <b>Goodbye ON</b>\n{_nb_L}\n\n✅ Ab group se jane wale members ka goodbye message aayega! 👋\n\n💡 Band karne ke liye:\n<code>/offbye</code>\n\n{_nb_L}\n{_nb_SM} @notCoder2006 {_nb_CK}\n{_nb_L}</blockquote>', parse_mode='HTML')

@bot.message_handler(commands=['leaved'])
def cmd_leaved_toggle(msg):
    """Group admin: /leaved on | /leaved off — bye/leave message toggle"""
    if msg.chat.type not in ['group', 'supergroup']:
        bot.reply_to(msg, '<blockquote> Ye command sirf group mein kaam karta hai!\n @notCoder2006</blockquote>', parse_mode='HTML')
        return
    uid = msg.from_user.id
    try:
        cm = bot.get_chat_member(msg.chat.id, uid)
        if cm.status not in ['administrator', 'creator'] and (not is_admin(uid)):
            bot.reply_to(msg, '<blockquote> Sirf group admin ya bot owner use kar sakta hai!\n @notCoder2006</blockquote>', parse_mode='HTML')
            return
    except:
        return
    parts = msg.text.strip().split()
    arg = parts[1].lower() if len(parts) > 1 else ''
    fname = msg.from_user.first_name or ''
    _L = '' * 10
    _CK = ''
    _SM = ''
    _BELL = ''
    _MUTE = ''
    try:
        if arg == 'off':
            set_group_bye_on(msg.chat.id, 0)
            bot.reply_to(msg, f"<blockquote>{_L}\n{_MUTE} <b>Leave Message OFF</b>\n{_L}\n\n❌ Ab koi member chhodega toh msg nahi aayega.\n\n👑 Admin: <a href='tg://user?id={uid}'>{fname}</a>\n💡 ON: <code>/leaved on</code>\n\n{_L}\n{_SM} @notCoder2006 {_CK}\n{_L}</blockquote>", parse_mode='HTML')
        elif arg == 'on':
            set_group_bye_on(msg.chat.id, 1)
            bot.reply_to(msg, f"<blockquote>{_L}\n{_BELL} <b>Leave Message ON</b>\n{_L}\n\n✅ Ab jab koi member chhodega toh msg aayega! 👋\n\n👑 Admin: <a href='tg://user?id={uid}'>{fname}</a>\n💡 OFF: <code>/leaved off</code>\n\n{_L}\n{_SM} @notCoder2006 {_CK}\n{_L}</blockquote>", parse_mode='HTML')
        else:
            _wr = c.execute('SELECT bye_on,welcome_on FROM group_welcome_settings WHERE group_id=?', (msg.chat.id,)).fetchone()
            _ws = ' ON' if _wr and _wr[1] == 1 else ' OFF'
            _bs = ' ON' if _wr and _wr[0] == 1 else ' OFF'
            bot.reply_to(msg, f'<blockquote>{_L}\nℹ️ <b>Group Settings</b>\n{_L}\n\n👋 Welcome : {_ws}\n🚪 Leave   : {_bs}\n\n• <code>/leaved on</code>  /  <code>/leaved off</code>\n• <code>/wel on</code>     /  <code>/wel off</code>\n\n{_L}\n{_SM} @notCoder2006 {_CK}\n{_L}</blockquote>', parse_mode='HTML')
    except Exception as _le:
        print(f'[LEAVED_TOGGLE] {_le}')
        try:
            bot.reply_to(msg, '<blockquote> Error. Bot ko group admin banao!\n @notCoder2006</blockquote>', parse_mode='HTML')
        except:
            pass

@bot.message_handler(commands=['setvideo'])
def cmd_setvideo(msg):
    """Owner: /setvideo - reply to a video to set as welcome video globally"""
    uid = msg.from_user.id
    if not is_admin(uid):
        try:
            bot.reply_to(msg, '<blockquote> Owner only command!\n @notCoder2006</blockquote>', parse_mode='HTML')
        except:
            pass
        return
    reply = msg.reply_to_message
    if not reply or not reply.video:
        bot.reply_to(msg, '<blockquote> <b>SET WELCOME VIDEO</b>\n\nKisi video ko reply karke /setvideo bhejo!\n\n @notCoder2006</blockquote>', parse_mode='HTML')
        return
    try:
        file_id = reply.video.file_id
        file_info = bot.get_file(file_id)
        file_path_remote = file_info.file_path
        r = requests.get(f'https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path_remote}', timeout=60)
        if r.status_code == 200:
            _SCRIPT_DIR2 = os.path.dirname(os.path.abspath(__file__))
            local_path = os.path.join(_SCRIPT_DIR2, f'welcome_video_{_BOT_ID}.mp4')
            with open(local_path, 'wb') as vf:
                vf.write(r.content)
            c.execute('UPDATE welcome_settings SET welcome_video=? WHERE id=1', (local_path,))
            conn.commit()
            bot.reply_to(msg, '<blockquote> <b>Welcome Video Set!</b>\nAb naye members ke welcome mein ye video aayega!\n\n @notCoder2006</blockquote>', parse_mode='HTML')
        else:
            bot.reply_to(msg, '<blockquote> Video download failed!\n @notCoder2006</blockquote>', parse_mode='HTML')
    except Exception as e:
        bot.reply_to(msg, f'<blockquote>❌ Error: {_safe_err(e)}\n⚡ @notCoder2006</blockquote>', parse_mode='HTML')

@bot.message_handler(commands=['setrules'])
def cmd_setrules(msg):
    if msg.chat.type not in ['group', 'supergroup']:
        return
    uid = msg.from_user.id
    try:
        cm = bot.get_chat_member(msg.chat.id, uid)
        if cm.status not in ['administrator', 'creator'] and (not is_admin(uid)):
            return
    except:
        return
    parts = msg.text.split(None, 1)
    if len(parts) < 2:
        bot.reply_to(msg, '<blockquote> Usage: <code>/setrules Rules text yahan likho</code>\n @notCoder2006</blockquote>', parse_mode='HTML')
        return
    rules = parts[1].strip()
    set_group_rules(msg.chat.id, rules)
    bot.reply_to(msg, f'<blockquote>✅ <b>Group Rules Set!</b>\n\n📋 {rules}\n\n⚡ @notCoder2006</blockquote>', parse_mode='HTML')
_join_dedup = {}

def _join_already_welcomed(cid, uid):
    """Return True agar last 5 seconds mein already welcome bheja gaya ho"""
    key = f'{cid}:{uid}'
    now = time.time()
    last = _join_dedup.get(key, 0)
    if now - last < 5:
        return True
    _join_dedup[key] = now
    for k in list(_join_dedup.keys()):
        if now - _join_dedup[k] > 30:
            _join_dedup.pop(k, None)
    return False

@bot.message_handler(content_types=['new_chat_members'])
def h_newmember(m):
    cid = m.chat.id
    chat_title = m.chat.title or 'Group'
    for mb in m.new_chat_members:
        if mb.id == bot.get_me().id:
            add_group_to_db(cid, chat_title)
            continue
        if _join_already_welcomed(cid, mb.id):
            continue
        try:
            wel_on, rules = get_group_welcome(cid)
            if not wel_on:
                continue
        except:
            continue
        try:
            fname = mb.first_name or 'User'
            lname = mb.last_name or ''
            full_name = (fname + ' ' + lname).strip()
            uname = '@' + mb.username if mb.username else 'No Username'
            tgid = mb.id
            now = _now_ist()
            try:
                mem_count = bot.get_chat_members_count(cid)
            except:
                mem_count = '?'
            pic = None
            try:
                r_ph = requests.get(f'https://api.telegram.org/bot{BOT_TOKEN}/getUserProfilePhotos', params={'user_id': tgid, 'limit': 1}, timeout=8)
                if r_ph.status_code == 200:
                    photos = r_ph.json().get('result', {}).get('photos', [])
                    if photos and photos[0]:
                        file_id = photos[0][-1].get('file_id', '')
                        if file_id:
                            r_fi = requests.get(f'https://api.telegram.org/bot{BOT_TOKEN}/getFile', params={'file_id': file_id}, timeout=8)
                            if r_fi.status_code == 200:
                                fpath = r_fi.json().get('result', {}).get('file_path', '')
                                if fpath:
                                    pic = f'https://api.telegram.org/file/bot{BOT_TOKEN}/{fpath}'
            except Exception as ep:
                print(f'[WELCOME_PFP] {ep}')
            if rules:
                rules_section = '\n\n ʀᴜʟᴇꜱ:\n' + rules
            else:
                rules_section = '\n\n ʀᴜʟᴇꜱ:\n ꜱᴘᴀᴍ | ᴀʙᴜꜱᴇ | ᴘʀᴏᴍᴏ\n ʀᴇꜱᴘᴇᴄᴛ ᴀʟʟ\n ꜱᴛᴀʏ ᴀᴄᴛɪᴠᴇ '

            def _te(*args, **kwargs): return ""
            _E1 = '5465144557568010803'
            _E13 = '6204223208468521357'
            _E26 = '6151963850297051287'
            _E27 = '5976721148736445255'
            _E28 = '5976312108936076061'
            _E59 = '5465629669829128119'
            _E54 = '5465277838993141300'
            _E38 = '5039789890133296083'
            _E39 = '5041975203853239332'
            _E40 = '5041792560368977040'
            _E41 = '6201751179911766993'
            _TOP_R1 = _te(_E1) * 12
            _TOP_R2 = _te(_E1) * 12
            _MID = _te(_E59) * 9
            _BOT_BORDER = _te(_E54) * 10
            uname_disp = uname if uname != 'No Username' else f'<code>{tgid}</code>'
            gwimg, gwvid, gwvlist, gwstk = get_group_welcome_media(cid)
            try:
                c.execute('SELECT welcome_text FROM group_welcome_settings WHERE group_id=?', (cid,))
                gwtext_row = c.fetchone()
                gwtext = gwtext_row[0] if gwtext_row and gwtext_row[0] else None
            except:
                gwtext = None
            _GW_1 = '4958830950604604428'
            _GW_2 = '5465629669829128119'
            _GW_12 = '4956461073550017373'
            _GW_13 = '6147422674000808494'
            _GW_14 = '4958636483075376288'
            _GW_15 = '4958472587123360612'
            _GW_16 = '4956525562483967357'
            _GW_17 = '4958724224962265918'
            _GW_18 = '5465629669829128119'
            _GW_28 = '4958900559139570572'
            _GW_LOOP10 = _te(_GW_2) * 10
            if rules:
                _rules_lines = '\n'.join((f'• {r.strip()}' for r in rules.splitlines() if r.strip()))
            else:
                _rules_lines = f'{_te(_GW_14)} ɴᴏ ꜱᴘᴀᴍ\n{_te(_GW_15)} ɴᴏ ᴀʙᴜꜱᴇ\n{_te(_GW_16)} ʀᴇꜱᴩᴇᴄᴛ ᴇᴠᴇʀʏᴏɴᴇ'
            welcome_txt = f"<blockquote>{_te(_GW_1)} ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴛʜᴇ <b>{chat_title}</b> !!\n{_GW_LOOP10}\n{_te(_GW_12)}{_te('4958469026595472714')} ʜᴇʟʟᴏ 殺┋ <a href='tg://user?id={tgid}'><b>{full_name}</b></a> !!\n\n{_te(_GW_13)}  /help — ꜱᴀʀᴇ ᴄᴏᴍᴍᴀɴᴅ ᴅᴇᴋʜᴏ\n\n{_te(_GW_17)} ʀᴜʟᴇꜱ:\n{_rules_lines}\n\n{_GW_LOOP10}\n{_te(_GW_28)} ᴅᴇᴠᴇʟᴏᴩᴇʀ : @notCoder2006</blockquote>"
            if gwtext:
                welcome_txt = gwtext.replace('{name}', full_name).replace('{id}', str(tgid)).replace('{username}', uname).replace('{group}', chat_title)
            if gwstk:
                try:
                    bot.send_sticker(cid, gwstk)
                except:
                    pass
            sent = False
            if gwvlist:
                fid = get_next_group_video(cid)
                if fid:
                    try:
                        bot.send_video(cid, fid, caption=welcome_txt, parse_mode='HTML')
                        sent = True
                    except:
                        pass
            if not sent and gwvid:
                sent = _send_saved_group_media(cid, gwvid, 'video', welcome_txt)
            if not sent and gwimg:
                sent = _send_saved_group_media(cid, gwimg, 'photo', welcome_txt)
            if not sent and pic:
                try:
                    bot.send_photo(cid, pic, caption=welcome_txt, parse_mode='HTML')
                    sent = True
                except:
                    pass
            if not sent:
                for _retry in range(2):
                    try:
                        bot.send_message(cid, welcome_txt, parse_mode='HTML')
                        sent = True
                        break
                    except Exception as _we:
                        _err_str = str(_we)
                        if '429' in _err_str:
                            import re as _re429
                            _m429 = _re429.search('retry after (\\d+)', _err_str)
                            _wait = int(_m429.group(1)) if _m429 else 5
                            time.sleep(_wait + 1)
                        else:
                            break
            try:
                try:
                    bn = _get_bot_username()
                except:
                    bn = '𝙽𝚘𝚝 𝙲𝚘𝚍𝚎𝚛_bot'
                log_token_activity(tgid, full_name, mb.username or '', 0, 0, 'Group Join', bn)
            except:
                pass
        except Exception as e:
            _es = str(e)
            if '429' not in _es:
                print('[WELCOME] ' + _es)
            try:
                if '429' not in _es:
                    bot.send_message(cid, "<blockquote> ʜᴇʟʟᴏ <a href='tg://user?id='+str(mb.id)+><b>" + _html.escape(mb.first_name or 'User') + '</b></a>\n ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ <b>' + chat_title + '</b>\n @notCoder2006</blockquote>', parse_mode='HTML')
            except:
                pass

@bot.message_handler(content_types=['left_chat_member'])
def h_leftmember(m):
    mb = m.left_chat_member
    if not mb or mb.id == _get_bot_id():
        return
    cid = m.chat.id
    chat_title = m.chat.title or 'Group'
    try:
        fj_channels = get_force_join_channels()
        fj_ids = set()
        for entry in fj_channels:
            cid_str = str(entry[0])
            resolved = _resolve_chat_id(cid_str)
            if resolved:
                fj_ids.add(int(resolved))
        if int(cid) in fj_ids:
            _channel_check_cache.pop(mb.id, None)
            try:
                c.execute('UPDATE users SET joined_channel=0 WHERE user_id=?', (mb.id,))
                _orig_conn.commit()
            except:
                pass
            try:
                resolved_fj = _resolve_chat_id(str(cid)) or int(cid)
                _clear_join_request(mb.id, resolved_fj)
            except:
                pass
            try:
                mk = get_channels_keyboard(mb.id)
                bot.send_message(mb.id, f'<blockquote>⚠️ <b>ᴀʀᴇ ʙʜᴀɪ!</b>\n\nTune <b>{chat_title}</b> leave kar diya! 😢\n\nBot use karne ke liye wapis join karna hoga!\nJoin ke baad ✅ <b>I Joined — Verify</b> dabao.\n\n⚡ @notCoder2006</blockquote>', reply_markup=mk, parse_mode='HTML')
            except:
                pass
            return
    except:
        pass
    try:
        if not get_group_bye(cid):
            return
    except:
        return
    try:
        fname = mb.first_name or 'Hidden User'
        lname = mb.last_name or ''
        full_name = (fname + ' ' + lname).strip()
        uname = '@' + mb.username if mb.username else 'ʜɪᴅᴅᴇɴ ᴜꜱᴇʀ'
        now = _now_ist()
        try:
            mem_count = bot.get_chat_members_count(cid)
        except:
            mem_count = '?'

        def _te(*args, **kwargs): return ""
        _L1 = '4958830950604604428'
        _L2 = '5465629669829128119'
        _L12 = '4956461073550017373'
        _L13 = '6147422674000808494'
        _L14 = '4958636483075376288'
        _L15 = '4958472587123360612'
        _L16 = '4956525562483967357'
        _L17 = '4958724224962265918'
        _L28 = '4958900559139570572'
        _LOOP10 = _te(_L2) * 10
        left_txt = f"<blockquote>{_te(_L1)} <a href='tg://user?id={mb.id}'><b>{full_name}</b></a> ʜᴀꜱ ʟᴇꜰᴛ ᴛʜᴇ ɢʀᴏᴜᴩ 😢\n{_LOOP10}\n\n{_te(_L12)} ɴᴀᴍᴇ  : <b>{full_name}</b>\n{_te(_L13)} ɪᴅ    : <code>{mb.id}</code>\n{_te(_L14)} ᴜꜱᴇʀ  : {uname}\n\n{_te(_L17)} ɢʀᴏᴜᴩ : <b>{chat_title}</b>\n{_te(_L15)} ᴍᴇᴍʙᴇʀꜱ : <b>{mem_count}</b>\n{_te(_L16)} ᴛɪᴍᴇ  : {now}\n\n{_LOOP10}\n{_te(_L28)} ᴅᴇᴠᴇʟᴏᴩᴇʀ : @notCoder2006</blockquote>"
        bot.send_message(cid, left_txt, parse_mode='HTML')
        try:
            log_token_activity(mb.id, full_name, mb.username or '', 0, 0, 'Group Left', _get_bot_username())
        except:
            pass
    except Exception as e:
        print('[LEFT] ' + str(e))

@bot.callback_query_handler(func=lambda call: call.data.startswith('numpage_'))
def h_numpage(call):
    parts = call.data.split('_')
    if len(parts) < 3:
        bot.answer_callback_query(call.id)
        return
    try:
        owner_uid = int(parts[1])
        page = int(parts[2])
    except:
        bot.answer_callback_query(call.id)
        return
    uid = call.from_user.id
    if uid != owner_uid:
        bot.answer_callback_query(call.id, ' Sirf search karne wala use kar sakta hai!')
        return
    cache = _num_cache.get(uid)
    if not cache:
        bot.answer_callback_query(call.id, ' Data expire ho gaya. Dobara search karo.')
        return
    bot.answer_callback_query(call.id)
    data = cache['data']
    num = cache['num']
    total = cache['total']
    page = max(1, min(page, total))
    rtxt, _, has_prev, has_next = fmt_number_page(data, num, page, per_page=2, uid=uid, elapsed=cache.get('elapsed'))
    _num_cache[uid]['page'] = page
    total_pages = cache.get('total') or 1
    try:
        _, total_pages, _, _ = fmt_number_page(data, num, 1, per_page=2, uid=uid, elapsed=cache.get('elapsed'))
        _num_cache[uid]['total'] = total_pages
    except Exception:
        pass
    mk_pg = _num_page_markup(uid, page, total_pages)
    try:
        bot.edit_message_text(rtxt, call.message.chat.id, call.message.message_id, reply_markup=mk_pg, parse_mode='HTML')
    except:
        bot.send_message(call.message.chat.id, rtxt, reply_markup=mk_pg, parse_mode='HTML')

@bot.callback_query_handler(func=lambda call: call.data.startswith('un_more_'))
def h_un_more_callback(call):
    """Show More Details button for username lookup"""
    bot.answer_callback_query(call.id, ' Loading full details...')
    uid = call.from_user.id
    d = call.data
    parts = d.split('_')
    try:
        _orig_uid = int(parts[2])
        _orig_mid = parts[3]
    except:
        _orig_uid = uid
        _orig_mid = ''
    _key = f'unres_{_orig_uid}_{_orig_mid}'
    cached = _user_temp_cache.get(_key)
    if not cached:
        bot.answer_callback_query(call.id, ' Data expired! Search again.', show_alert=True)
        return
    res = cached.get('res')
    query = cached.get('query', '')
    now = _now_ist()
    rtxt, _ = _fmt_tg_user_short(res, query, now)
    if isinstance(rtxt, tuple):
        rtxt = rtxt[0]
    try:
        bot.send_message(call.message.chat.id, rtxt, parse_mode='HTML')
    except Exception as _e:
        print(f'[UN_MORE_CB] {_safe_err(_e)}')

@bot.callback_query_handler(func=lambda call: True)
def h_callback(call):
    uid = call.from_user.id
    d = call.data
    fname = _html.escape(call.from_user.first_name or 'User')
    uname_tg = call.from_user.username or ''
    if is_identifier_blocked(str(uid)):
        bot.answer_callback_query(call.id, ' Blocked!')
        return
    if d == 'show_premium_plans':
        bot.answer_callback_query(call.id)

        def _te(*args, **kwargs): return ""
        _L = _te('5465629669829128119') * 11
        plans_txt = f"<blockquote>{_L}\n{_te('6285328937094485878')} {_te('5312361253610475399')} 𝗧ʜᴇ 𝗡ᴏᴛ 𝗖ᴏᴅᴇʀ {_te('6113891550788324241')} 𝗜ɴꜰᴏ 𝗕ᴏᴛ ᴩʀᴇᴍɪᴜᴍ ᴜᴩɢʀᴀᴅᴇ\n{_L}\nOWNER SE CONTACT KARO\n\n{_te('5312361253610475399')} ᴘʟᴀɴꜱ\n├ 💳 20 ᴄʀᴇᴅɪᴛꜱ : ₹60\n├ 💳 50 ᴄʀᴇᴅɪᴛꜱ : ₹100\n└ 💳 100 ᴄʀᴇᴅɪᴛꜱ : ₹200\n└ 💳 200 ᴄʀᴇᴅɪᴛꜱ : ₹500\n\n{_L}\n{_te('6037622221625626773')} {_te('5258204546391351475')} ꜱᴛᴇᴩꜱ\n➤ ꜱᴄᴀɴ Qʀ ᴀɴᴅ ᴘᴀʏ\n➤ ꜱᴇɴᴅ {_te('5377660214096974712')} Tʀᴀɴꜱꜰᴇʀ ɪᴅ\n➤ ꜱᴇɴᴅ ꜱᴄʀᴇᴇɴꜱʜᴏᴛ ᴛᴏ ᴀᴅᴍɪɴ\n\n{_te('6204263190319081111')} ʙᴏᴛ ᴍᴀᴅᴇ ʙʏ : @notCoder2006 {_te('6147565374289220368')}</blockquote>"
        back_mk = InlineKeyboardMarkup()
        back_mk.add(_IKB('⬅ ʙᴀᴄᴋ', style='danger', callback_data='back_to_nocredits'))
        try:
            bot.edit_message_text(plans_txt, call.message.chat.id, call.message.message_id, reply_markup=back_mk, parse_mode='HTML')
        except:
            bot.send_message(uid, plans_txt, reply_markup=back_mk, parse_mode='HTML')
        return
    if d == 'back_to_nocredits':
        bot.answer_callback_query(call.id)
        txt, mk = no_credits_msg(uid)
        try:
            bot.edit_message_text(txt, call.message.chat.id, call.message.message_id, reply_markup=mk, parse_mode='HTML')
        except:
            bot.send_message(uid, txt, reply_markup=mk, parse_mode='HTML')
        return
    if d == 'verify_channels':
        _channel_check_cache.pop(uid, None)
        _is_group_verify = call.message.chat.type in ['group', 'supergroup']

        def _bot_has_channel_access():
            chs = get_force_join_channels()
            if not chs:
                return True
            try:
                me = bot.get_me()
                bot_id = me.id
            except Exception:
                bot_id = None
            checked = False
            for entry in chs:
                cid_str = str(entry[0]).strip()
                if cid_str.startswith('https://'):
                    continue
                cid_val = _resolve_chat_id(cid_str)
                if not cid_val:
                    continue
                checked = True
                try:
                    bot.get_chat(cid_val)
                    if bot_id is not None:
                        try:
                            bot.get_chat_member(cid_val, bot_id)
                        except Exception:
                            pass
                    return True
                except Exception:
                    continue
            return (not checked)
        verified = check_channel(uid)
        if verified:
            bot.answer_callback_query(call.id, ' Verified!')
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except:
                pass
            if _is_group_verify:
                try:
                    bot.send_message(call.message.chat.id, f"<blockquote>✅ <a href='tg://user?id={uid}'><b>{call.from_user.first_name}</b></a> verified! Ab bot use kar sakte ho!</blockquote>", parse_mode='HTML')
                except:
                    pass
            else:
                _pref = user_state.pop(uid, None)
                _pending_ref = _pref.get('pending_ref') if isinstance(_pref, dict) else None
                user = get_user(uid)
                nm = user[2] if user else 'User'
                cr = get_credits(uid)
                if not user:
                    add_user(uid, call.from_user.username or '', call.from_user.first_name or 'User', _pending_ref)
                    user = get_user(uid)
                    nm = user[2] if user else 'User'
                    cr = get_credits(uid)
                elif _pending_ref and (not get_user(uid)):
                    add_user(uid, call.from_user.username or '', call.from_user.first_name or 'User', _pending_ref)
                try:
                    rl = f'https://t.me/{_get_bot_username()}?start={uid}'
                except:
                    rl = '--'
                _wmk = InlineKeyboardMarkup()
                _wmk.add(_IKB('ꜱʜᴀʀᴇ', style='success', url=f'https://t.me/share/url?url={rl}&amp;text=Join+this+amazing+Info+Bot!'))
                wtxt_v = format_welcome(uid, nm, cr, call.from_user.username or '')
                wtxt_v_cap = _safe_caption(wtxt_v, 1024)
                st_v = get_welcome_settings()
                wvid_v = st_v[4] if st_v else None
                wimg_v = st_v[3] if st_v else None
                _v_sent = False
                _wv_fid_v = _welcome_fileid_cache.get('video')
                _wi_fid_v = _welcome_fileid_cache.get('image')
                if _wv_fid_v:
                    try:
                        bot.send_video(uid, _wv_fid_v, caption=wtxt_v_cap, reply_markup=kb_p1(uid), parse_mode='HTML', has_spoiler=True, message_effect_id='5046509860389126442')
                        _v_sent = True
                    except:
                        _welcome_fileid_cache.pop('video', None)
                if not _v_sent and _wi_fid_v:
                    try:
                        bot.send_photo(uid, _wi_fid_v, caption=wtxt_v_cap, reply_markup=kb_p1(uid), parse_mode='HTML', has_spoiler=True, message_effect_id='5046509860389126442')
                        _v_sent = True
                    except:
                        _welcome_fileid_cache.pop('image', None)
                if not _v_sent and wvid_v and os.path.exists(wvid_v):
                    try:
                        with open(wvid_v, 'rb') as _fv:
                            bot.send_video(uid, _fv, caption=wtxt_v_cap, reply_markup=kb_p1(uid), parse_mode='HTML', has_spoiler=True, message_effect_id='5046509860389126442')
                            _v_sent = True
                    except:
                        pass
                if not _v_sent and wimg_v and os.path.exists(wimg_v):
                    try:
                        with open(wimg_v, 'rb') as _fi:
                            bot.send_photo(uid, _fi, caption=wtxt_v_cap, reply_markup=kb_p1(uid), parse_mode='HTML', has_spoiler=True, message_effect_id='5046509860389126442')
                            _v_sent = True
                    except:
                        pass
                if not _v_sent:
                    try:
                        _send_react(uid, wtxt_v, reply_markup=kb_p1(uid), parse_mode='HTML', message_effect_id='5046509860389126442')
                    except:
                        import re as _rev
                        bot.send_message(uid, _rev.sub('<[^>]+>', '', wtxt_v), reply_markup=kb_p1(uid))
        else:
            _mk_still = get_channels_keyboard(uid)
            if _mk_still:
                bot.answer_callback_query(call.id, ' Abhi bhi kuch channels join nahi kiye!')
                try:
                    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=_mk_still)
                except:
                    pass
            else:
                bot.answer_callback_query(call.id, ' Join all channels first!')
        return
    if d == 'noop':
        bot.answer_callback_query(call.id)
        return
    if d == 'redeem_credit_code':
        bot.answer_callback_query(call.id)
        user_state[uid] = S_REDEEM
        bot.send_message(uid, '<blockquote> <b>ᴄʀᴇᴅɪᴛ ᴄᴏᴅᴇ</b>\n\n Code bhejo:\nExample: <code>NOT CODER-XXXXXX</code>\n\n @notCoder2006</blockquote>', parse_mode='HTML')
        return
    if d == 'redeem_premium_code':
        bot.answer_callback_query(call.id)
        user_state[uid] = S_PREM_REDEEM
        bot.send_message(uid, '<blockquote> <b>ᴘʀᴇᴍɪᴜᴍ ᴄᴏᴅᴇ</b>\n\n Code bhejo:\nExample: <code>NOT_CODER-PR-XXXXXX</code>\n\n @notCoder2006</blockquote>', parse_mode='HTML')
        return
    if d == 'refer_no_points' or d.startswith('refer_need_'):
        bot.answer_callback_query(call.id)
        try:
            lnk = f'https://t.me/{_get_bot_username()}?start={uid}'
        except:
            lnk = f'https://t.me/bot?start={uid}'
        try:
            _coins_row = c.execute('SELECT coins FROM users WHERE user_id=?', (uid,)).fetchone()
            coins = _coins_row[0] if _coins_row and _coins_row[0] else 0
        except:
            coins = 0
        if d.startswith('refer_need_'):
            try:
                tier_cost = int(d.split('_')[2])
                needed = max(0, tier_cost - coins)
            except:
                tier_cost = 5
                needed = max(0, 5 - coins)
        else:
            tier_cost = 5
            needed = max(0, 5 - coins)
        txt = f'<blockquote>╭━━━━━━━━━━━━━━━━━━━━━━━━━━━━✦\n│ 🔴 <b>ɪɴꜱᴜꜰꜰɪᴄɪᴇɴᴛ ᴩᴏɪɴᴛꜱ</b>\n╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━✦\n\n🎫 Tumhare Refer Points: <b>{coins}</b>\n💡 Is plan ke liye chahiye: <b>{tier_cost} 🎫</b>\n📊 Aur chahiye: <b>{needed} 🎫</b>\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━\n👥 Refer karo → Points pao → Premium lo!\n\n🔗 Tera refer link:\n<code>{lnk}</code>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━\n⚡ @notCoder2006</blockquote>'
        mk_rp = InlineKeyboardMarkup()
        mk_rp.add(_IKB(' ʀᴇꜰᴇʀ ᴋᴀʀᴏ — ᴩᴏɪɴᴛꜱ ᴋᴀᴍᴀᴏ', style='primary', url=f'https://t.me/share/url?url={lnk}&text=Join+this+amazing+info+bot!'))
        mk_rp.add(_IKB(' ᴄʟᴏꜱᴇ', style='danger', callback_data='close_prem_claim'))
        try:
            bot.edit_message_text(txt, call.message.chat.id, call.message.message_id, reply_markup=mk_rp, parse_mode='HTML')
        except:
            bot.send_message(uid, txt, reply_markup=mk_rp, parse_mode='HTML')
        return
    if d == 'close_prem_claim':
        bot.answer_callback_query(call.id)
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass
        return
    if d == 'show_my_credits':
        bot.answer_callback_query(call.id)
        cr = get_credits(uid)
        refs = get_referral_count(uid)
        user = get_user(uid)
        is_prem = user[7] == 1 if user else False
        prem_str = str(cr)
        spin_done = not can_claim_daily(uid)
        spin_str = 'Claimed' if spin_done else 'Available'
        try:
            lnk = 'https://t.me/' + _get_bot_username() + '?start=' + str(uid)
        except:
            lnk = 'https://t.me/bot?start=' + str(uid)
        mk_sc = InlineKeyboardMarkup()
        mk_sc.add(_IKB(f' Refer Karo +{get_referral_bonus()} Credits', style='success', url='https://t.me/share/url?url=' + lnk + '&text=Join+karo!'))
        _smc = '<blockquote>━━━━━━━━━━━━━━━━━━━━━━\n <b>MY CREDITS</b>\n━━━━━━━━━━━━━━━━━━━━━━\n\n Credits      : <b>' + prem_str + '</b>\n Total Refers : <b>' + str(refs) + '</b>\n Daily Spin   : ' + spin_str + '\n\n━━━━━━━━━━━━━━━━━━━━━━\n Refer Link:\n<code>' + lnk + '</code>\n━━━━━━━━━━━━━━━━━━━━━━\n @notCoder2006</blockquote>'
        try:
            bot.send_message(uid, _smc, reply_markup=mk_sc, parse_mode='HTML')
        except:
            pass
        return
    if d.startswith('apiurl_'):
        if uid != OWNER_ID:
            bot.answer_callback_query(call.id, ' Sirf owner!')
            return
        bot.answer_callback_query(call.id)
        if d == 'apiurl_back':
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except:
                pass
            bot.send_message(uid, '<blockquote> <b>Admin P1</b></blockquote>', reply_markup=kb_admin_p1(), parse_mode='HTML')
            return
        if d.startswith('apiurl_sel_'):
            api_key = d[len('apiurl_sel_'):]
            api_info = next(((k, lbl, url) for k, lbl, url in _BOT_APIS if k == api_key), None)
            if not api_info:
                bot.answer_callback_query(call.id, ' Unknown API')
                return
            _, api_label, default_url = api_info
            custom_url = _get_api_custom_url(api_key)
            current_url = custom_url if custom_url else default_url
            source = ' Custom' if custom_url else ' Default'
            txt = f'<blockquote>🔗 <b>{api_label}</b>\n━━━━━━━━━━━━━━━━━━\n\nKey: <code>{api_key}</code>\nSource: {source}\n\n<b>Current URL:</b>\n<code>{current_url}</code>\n\n<i>Note: URL mein {{}} placeholder hona chahiye.</i>\n⚡ @notCoder2006</blockquote>'
            mk = InlineKeyboardMarkup()
            mk.add(_IKB(' URL Change Karo', style='success', callback_data=f'apiurl_change_{api_key}'))
            if custom_url:
                mk.add(_IKB(' Reset to Default', style='danger', callback_data=f'apiurl_reset_{api_key}'))
            mk.add(_IKB('⬅ API List', style='primary', callback_data='apiurl_list'))
            try:
                bot.edit_message_text(txt, call.message.chat.id, call.message.message_id, reply_markup=mk, parse_mode='HTML')
            except:
                bot.send_message(uid, txt, reply_markup=mk, parse_mode='HTML')
            return
        if d.startswith('apiurl_change_'):
            api_key = d[len('apiurl_change_'):]
            api_info = next(((k, lbl, url) for k, lbl, url in _BOT_APIS if k == api_key), None)
            if not api_info:
                bot.answer_callback_query(call.id, ' Unknown API')
                return
            _, api_label, _ = api_info
            mk_cancel = InlineKeyboardMarkup()
            mk_cancel.add(_IKB(' Cancel', style='danger', callback_data=f'apiurl_sel_{api_key}'))
            prompt = bot.send_message(uid, f'<blockquote>✏️ <b>{api_label}</b>\n\nNaya URL type karke bhejo:\n\nFormat: <code>https://example.com/api?q={{}}&key=XYZ</code>\n\n⚠️ {{}} placeholder zaroori hai!\n<i>Cancel karne ke liye button dabao.</i></blockquote>', reply_markup=mk_cancel, parse_mode='HTML')
            user_state[uid] = {'state': 'API_URL_INPUT', 'api_key': api_key, 'api_label': api_label, 'prompt_msg_id': prompt.message_id}
            return
        if d.startswith('apiurl_reset_'):
            api_key = d[len('apiurl_reset_'):]
            try:
                c.execute('DELETE FROM api_keys WHERE api_name=?', (api_key,))
                conn.commit()
            except:
                pass
            api_info = next(((k, lbl, url) for k, lbl, url in _BOT_APIS if k == api_key), None)
            lbl = api_info[1] if api_info else api_key
            bot.send_message(uid, f'<blockquote>✅ <b>{lbl}</b> reset to default!\n⚡ @notCoder2006</blockquote>', parse_mode='HTML')
            _send_bot_api_urls_menu(uid)
            return
        if d == 'apiurl_list':
            _send_bot_api_urls_menu(uid, call.message.message_id)
            return
        return
    if d.startswith('apikey_'):
        if uid != OWNER_ID:
            bot.answer_callback_query(call.id, ' Sirf owner!')
            return
        bot.answer_callback_query(call.id)
        if d == 'apikey_back':
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except:
                pass
            bot.send_message(uid, '<blockquote> <b>Admin P1</b></blockquote>', reply_markup=kb_admin_p1(), parse_mode='HTML')
            return
        if d == 'apikey_list':
            _send_bot_api_keys_menu(uid, call.message.message_id)
            return
        if d.startswith('apikey_sel_'):
            key_name = d[len('apikey_sel_'):]
            key_info = next(((k, lbl, dk) for k, lbl, dk in _BOT_API_KEYS if k == key_name), None)
            if not key_info:
                bot.answer_callback_query(call.id, ' Unknown Key')
                return
            _, key_label, default_key = key_info
            custom_key = _get_api_custom_key(key_name)
            current_key = custom_key if custom_key else default_key
            source = ' Custom' if custom_key else ' Default'
            masked = current_key[:6] + '***' + current_key[-4:] if len(current_key) > 10 else current_key
            txt2 = f'<blockquote>🔑 <b>{key_label}</b>\n━━━━━━━━━━━━━━━━━━\n\nKey Name: <code>{key_name}</code>\nSource: {source}\n\n<b>Current Key:</b>\n<code>{masked}</code>\n\n<i>Naya key set karne ke liye button dabao.</i>\n⚡ @notCoder2006</blockquote>'
            mk2 = InlineKeyboardMarkup()
            mk2.add(_IKB(' Key Change Karo', style='success', callback_data=f'apikey_change_{key_name}'))
            if custom_key:
                mk2.add(_IKB(' Reset to Default', style='danger', callback_data=f'apikey_reset_{key_name}'))
            mk2.add(_IKB('⬅ Key List', style='primary', callback_data='apikey_list'))
            try:
                bot.edit_message_text(txt2, call.message.chat.id, call.message.message_id, reply_markup=mk2, parse_mode='HTML')
            except:
                bot.send_message(uid, txt2, reply_markup=mk2, parse_mode='HTML')
            return
        if d.startswith('apikey_change_'):
            key_name = d[len('apikey_change_'):]
            key_info = next(((k, lbl, dk) for k, lbl, dk in _BOT_API_KEYS if k == key_name), None)
            if not key_info:
                bot.answer_callback_query(call.id, ' Unknown Key')
                return
            _, key_label, _ = key_info
            mk_cancel = InlineKeyboardMarkup()
            mk_cancel.add(_IKB(' Cancel', style='danger', callback_data=f'apikey_sel_{key_name}'))
            prompt = bot.send_message(uid, f'<blockquote>✏️ <b>{key_label}</b>\n\nNaya API key type karke bhejo:\n\nExample: <code>SH4DAW-NEWKEY</code>\n\n<i>Cancel karne ke liye button dabao.</i></blockquote>', reply_markup=mk_cancel, parse_mode='HTML')
            user_state[uid] = {'state': 'API_KEY_INPUT', 'key_name': key_name, 'key_label': key_label, 'prompt_msg_id': prompt.message_id}
            return
        if d.startswith('apikey_reset_'):
            key_name = d[len('apikey_reset_'):]
            try:
                c.execute("UPDATE api_keys SET api_key='' WHERE api_name=?", (key_name,))
                conn.commit()
            except:
                pass
            key_info = next(((k, lbl, dk) for k, lbl, dk in _BOT_API_KEYS if k == key_name), None)
            lbl = key_info[1] if key_info else key_name
            default_k = key_info[2] if key_info else '—'
            bot.send_message(uid, f'<blockquote>✅ <b>{lbl}</b> default pe reset!\nDefault: <code>{default_k}</code>\n⚡ @notCoder2006</blockquote>', parse_mode='HTML')
            _send_bot_api_keys_menu(uid)
            return
        return
    if d == 'back_to_main':
        user_state[uid] = S_NONE
        bot.send_message(uid, '<blockquote>⬇ ᴍᴀɪɴ ᴍᴇɴᴜ</blockquote>', reply_markup=kb_p1(uid), parse_mode='HTML')
        bot.answer_callback_query(call.id)
        return
    if d == 'menu_p2':
        bot.answer_callback_query(call.id)
        try:
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=kb_menu_p2(uid))
        except Exception:
            pass
        return
    if d == 'menu_p1':
        bot.answer_callback_query(call.id)
        try:
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=kb_menu_p1(uid))
        except Exception:
            pass
        return
    if d == 'menu_close':
        bot.answer_callback_query(call.id)
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception:
            pass
        return
    smap = {'menu_number': S_NUM, 'menu_username': S_USER, 'menu_tgid': S_TID, 'menu_aadhar': S_ADH, 'menu_instagram': S_INSTA, 'menu_freefire': S_FF, 'menu_freefire_like': S_FF_LIKE_UID, 'menu_vehicle': S_VEH}
    prompt_map = {'menu_number': ' 10-digit number bhejo:', 'menu_username': ' @username bhejo:', 'menu_tgid': ' Telegram ID bhejo:', 'menu_aadhar': ' Aadhar number bhejo:', 'menu_instagram': ' Instagram username bhejo:', 'menu_freefire': ' FF UID bhejo:', 'menu_freefire_like': ' FF UID bhejo:', 'menu_vehicle': ' RC number bhejo:'}
    if d == 'menu_spin':
        bot.answer_callback_query(call.id)
        if is_admin(uid) or can_claim_daily(uid):
            try:
                dm = bot.send_dice(uid, emoji=_get_spin_emoji())
                time.sleep(2)
                cw = {1: 1, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5}.get(getattr(getattr(dm, 'dice', None), 'value', 1), 1)
                c.execute('UPDATE users SET credits=COALESCE(credits,0)+? WHERE user_id=?', (cw, uid))
                if not is_admin(uid):
                    c.execute('INSERT OR IGNORE INTO daily_claims VALUES(?,?)', (uid, datetime.now().strftime('%Y-%m-%d')))
                conn.commit()
                _user_cache.pop(uid, None)
                total = get_credits(uid)
                bot.send_message(uid, f'<blockquote>━━━━━━━━━━━━━━━━━━━━━━━━━━\n🎁 <b>ᴅᴀɪʟʏ ꜱᴘɪɴ</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n🎉 Won: <code>+{cw}</code> credits!\n💰 Total: <code>{total}</code>\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n⚡ @notCoder2006</blockquote>', parse_mode='HTML')
            except Exception as _spin_cb_e:
                bot.send_message(uid, f'<blockquote>❌ Spin error: {_safe_err(_spin_cb_e)}</blockquote>', parse_mode='HTML')
        else:
            bot.send_message(uid, '<blockquote> Already claimed today!\n Kal wapis aao!\n @notCoder2006</blockquote>', parse_mode='HTML')
        return
    if d == 'menu_redeem':
        bot.answer_callback_query(call.id)
        user_state[uid] = S_REDEEM
        bot.send_message(uid, '<blockquote>🎫 <b>ᴄʀᴇᴅɪᴛ ᴄᴏᴅᴇ</b>\n\nCode bhejo:\nExample: <code>NOT CODER-XXXXXX</code>\n\n @notCoder2006</blockquote>', parse_mode='HTML')
        return
    if d == 'menu_refer':
        bot.answer_callback_query(call.id)
        try:
            rl = f'https://t.me/{_get_bot_username()}?start={uid}'
        except Exception:
            rl = f'https://t.me/bot?start={uid}'
        refs = get_referral_count(uid)
        mk_ref = InlineKeyboardMarkup()
        mk_ref.add(_IKB(f' ʀᴇꜰᴇʀ ᴋᴀʀᴏ — +{get_referral_bonus()} ᴄʀᴇᴅɪᴛꜱ', style='success', url=f'https://t.me/share/url?url={rl}&text=Join+this+amazing+bot!'))
        bot.send_message(uid, f'<blockquote>━━━━━━━━━━━━━━━━━━\n👥 <b>ʀᴇꜰᴇʀ & ᴇᴀʀɴ</b>\n━━━━━━━━━━━━━━━━━━\n\n📊 Total Referrals: <b>{refs}</b>\n\n🔗 Your referral link:\n<code>{rl}</code>\n\n💰 Per referral: +{get_referral_bonus()} credits\n━━━━━━━━━━━━━━━━━━\n⚡ @notCoder2006</blockquote>', reply_markup=mk_ref, parse_mode='HTML')
        return
    if d == 'menu_support':
        bot.answer_callback_query(call.id)
        mk_support = InlineKeyboardMarkup()
        mk_support.add(_IKB(' Contact @notCoder2006', url='https://t.me/@notCoder2006'))
        mk_support.add(_IKB(' Join @notCoder2006', url='https://t.me/𝙽𝚘𝚝 𝙲𝚘𝚍𝚎𝚛'))
        bot.send_message(uid, '<blockquote>━━━━━━━━━━━━━━━━━━\n👑 <b>ᴏᴡɴᴇʀ / ꜱᴜᴩᴩᴏʀᴛ</b>\n━━━━━━━━━━━━━━━━━━\n\nɪꜰ ʏᴏᴜ ꜰᴀᴄᴇ ᴀɴʏ ɪꜱꜱᴜᴇꜱ, ᴄᴏɴᴛᴀᴄᴛ ᴏᴜʀ ᴀᴅᴍɪɴ:\n🌐 @notCoder2006\n⭐ 5908171064\n━━━━━━━━━━━━━━━━━━\n⚡ @notCoder2006</blockquote>', reply_markup=mk_support, parse_mode='HTML')
        return
    if d == 'menu_leaderboard':
        bot.answer_callback_query(call.id)
        try:
            week_start = (datetime.now() - timedelta(days=datetime.now().weekday())).strftime('%Y-%m-%d')
            rows = c.execute('SELECT u.user_id,u.first_name,u.username,COUNT(r.id) AS cnt FROM users u LEFT JOIN referrals r ON u.user_id=r.referrer AND r.date >= ? GROUP BY u.user_id ORDER BY cnt DESC LIMIT 10', (week_start,)).fetchall()
            lines = []
            for i, row in enumerate(rows, 1):
                rid, name, username, cnt = row
                label = f'@{username}' if username else (name or str(rid))
                lines.append(f'<b>{i}.</b> {label} — <code>{cnt}</code> referrals')
            if not lines:
                lines = ['No referral data yet.']
            bot.send_message(uid, '<blockquote>━━━━━━━━━━━━━━━━━━\n🏆 <b>ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ</b>\n━━━━━━━━━━━━━━━━━━\n\n' + '\n'.join(lines) + '\n━━━━━━━━━━━━━━━━━━\n⚡ @notCoder2006</blockquote>', parse_mode='HTML')
        except Exception as _lb_e:
            bot.send_message(uid, f'<blockquote>❌ Leaderboard error: {_safe_err(_lb_e)}</blockquote>', parse_mode='HTML')
        return
    if d in smap:
        bot.answer_callback_query(call.id)
        user_state[uid] = smap[d]
        _cr_inline = get_credits(uid)
        _rate_map = {'menu_number': '1', 'menu_username': '1', 'menu_tgid': '1', 'menu_aadhar': '1', 'menu_instagram': '1', 'menu_freefire': '1', 'menu_freefire_like': '2', 'menu_vehicle': '1', 'menu_vehicle': '1'}
        _prompt_full_map = {'menu_number': f'📱 ꜱᴇɴᴅ <b>10-ᴅɪɢɪᴛ ᴍᴏʙɪʟᴇ ɴᴜᴍʙᴇʀ</b>\nᴇxᴀᴍᴩʟᴇ: <code>9876543210</code>', 'menu_username': f'🔍 ꜱᴇɴᴅ <b>@username</b> ʏᴀ <b>TG ID</b>\nᴇxᴀᴍᴩʟᴇ: <code>@durov</code>', 'menu_tgid': f'🆔 ꜱᴇɴᴅ <b>Telegram ID</b>\nᴇxᴀᴍᴩʟᴇ: <code>123456789</code>', 'menu_aadhar': f'🆔 ꜱᴇɴᴅ <b>12-ᴅɪɢɪᴛ Aadhar</b>\nᴇxᴀᴍᴩʟᴇ: <code>649964855626</code>', 'menu_instagram': f'📸 ꜱᴇɴᴅ <b>Instagram Username</b>\nᴇxᴀᴍᴩʟᴇ: <code>cristiano</code>', 'menu_freefire': f'🎮 ꜱᴇɴᴅ <b>FF UID</b>\nᴇxᴀᴍᴩʟᴇ: <code>1382401870</code>', 'menu_freefire_like': f'❤️ ꜱᴇɴᴅ <b>FF UID</b>\nᴇxᴀᴍᴩʟᴇ: <code>1382401870</code>', 'menu_vehicle': f'🚗 ꜱᴇɴᴅ <b>RC Number</b>\nᴇxᴀᴍᴩʟᴇ: <code>MH12AB1234</code>'}
        _rate = _rate_map.get(d, '1')
        _ptext = _prompt_full_map.get(d, 'Value bhejo:')
        bot.send_message(uid, f'<blockquote>{_ptext}\n\n💰 ꜱᴇᴀʀᴄʜ ʀᴀᴛᴇ :- <b>{_rate} ᴄʀᴇᴅɪᴛ</b>\n💳 ᴀᴀᴩᴋᴇ ᴄʀᴇᴅɪᴛꜱ :- <b>{_cr_inline}</b>\n\n⚡ ʙᴏᴛ ᴍᴀᴅᴇ ʙʏ : @notCoder2006</blockquote>', parse_mode='HTML')
        return
    if d == 'menu_mycredits':
        bot.answer_callback_query(call.id)
        cr = get_credits(uid)
        refs = get_referral_count(uid)
        user_row = get_user(uid)
        is_prem = bool(user_row[7]) if user_row else False
        spin_done = not can_claim_daily(uid)
        spin_str = ' ᴄʟᴀɪᴍᴇᴅ' if spin_done else ' ᴀᴠᴀɪʟᴀʙʟᴇ'
        prem_str = ' ᴜɴʟɪᴍɪᴛᴇᴅ' if is_prem else str(cr)
        try:
            rl = f'https://t.me/{_get_bot_username()}?start={uid}'
        except:
            rl = f'https://t.me/bot?start={uid}'
        rl_short = rl
        mk2 = InlineKeyboardMarkup()
        mk2.add(_IKB(f' ʀᴇꜰᴇʀ ᴋᴀʀᴏ — +{get_referral_bonus()} ᴄʀᴇᴅɪᴛꜱ', style='success', url=f'https://t.me/share/url?url={rl_short}&text=Join+karo+is+amazing+bot!'))
        _mc_txt = f"<blockquote>━━━━━━━━━━━━━━━━━━━━━━\n╭─── 💰 <b>ᴍʏ ᴄʀᴇᴅɪᴛꜱ</b> ───╮\n━━━━━━━━━━━━━━━━━━━━━━\n\n💰 ᴄʀᴇᴅɪᴛꜱ       : <b>{prem_str}</b>\n🎁 ᴅᴀɪʟʏ ꜱᴩɪɴ   : {spin_str}\n💎 ᴩʀᴇᴍɪᴜᴍ      : {('<b>ᴜɴʟɪᴍɪᴛᴇᴅ</b>' if is_prem else 'ɴᴏ')}\n\n━━━━━━━━━━━━━━━━━━━━━━\n╭━━━━━━━━━━━━━━━✦\n│ 👥 ʀᴇꜰᴇʀʀᴀʟꜱ\n╰━━━━━━━━━━━━━━━✦\n\n🔄 ʀᴇꜰᴇʀ ᴋʀᴏ → +{get_referral_bonus()} ᴄʀᴇᴅɪᴛ ᴩᴀᴏ!\n\n📊 ᴛᴏᴛᴀʟ ʀᴇꜰᴇʀʀᴀʟꜱ : <b>{refs}</b>\n\n🔗 ʀᴇꜰᴇʀ ʟɪɴᴋ :\n{rl_short}\n━━━━━━━━━━━━━━━━━━━━━━\n💰 ᴄʀᴇᴅɪᴛꜱ : {cr} | 👥 ʀᴇꜰᴇʀꜱ : {refs}\n🎁 ᴩᴇʀ ʀᴇꜰᴇʀʀᴀʟ : +{get_referral_bonus()} ᴄʀᴇᴅɪᴛꜱ\n━━━━━━━━━━━━━━━━━━━━━━\n⚡ @notCoder2006</blockquote>"
        try:
            bot.send_message(uid, _mc_txt, reply_markup=mk2, parse_mode='HTML')
        except Exception as _mce:
            print(f'[MENU_CREDITS] {_mce}')
        return
    if d == 'menu_channel':
        bot.answer_callback_query(call.id)
        chs = get_force_join_channels()
        if chs:
            mk = InlineKeyboardMarkup()
            for ch_id, ch_title, ch_url in chs:
                if ch_url and ch_url.startswith(('http://', 'https://')):
                    mk.add(_IKB(f'📢 {ch_title}', url=ch_url))
            bot.send_message(uid, '<blockquote> <b>Channels:</b></blockquote>', reply_markup=mk, parse_mode='HTML')
        else:
            bot.send_message(uid, '<blockquote> No channels set.</blockquote>', parse_mode='HTML')
        return
    if d == 'menu_helpinfo':
        bot.answer_callback_query(call.id)
        bot.send_message(uid, '<blockquote>ℹ <b>HELP</b>\n\n Number Info - Indian number lookup\n Username - TG username lookup\n TG ID - Telegram user info\n Bomber - SMS bomber\n FF Info - Free Fire player info\n FF Like - Send likes\n Vehicle - RC number lookup\n Daily Spin - Free credits daily\n\n @notCoder2006</blockquote>', parse_mode='HTML')
        return
    if d == 'menu_select_user':
        bot.answer_callback_query(call.id)
        bot.send_message(uid, '<blockquote> <b>ꜱᴇʟᴇᴄᴛ ᴜꜱᴇʀ</b>\nNeeche button dabao aur user select karo:</blockquote>', reply_markup=kb_select_user(), parse_mode='HTML')
        return
    if d == 'menu_bomber':
        bot.answer_callback_query(call.id)
        if not False:
            return
        user_state[uid] = S_BOMB
        bot.send_message(uid, '<blockquote> 10-digit number bhejo (bomber ke liye):\n<code>9876543210</code>\n @notCoder2006</blockquote>', parse_mode='HTML')
        return
    if d.startswith('grp_cls_'):
        try:
            owner_uid = int(d[len('grp_cls_'):])
            if uid != owner_uid:
                bot.answer_callback_query(call.id, ' Sirf button dabane wala close kar sakta hai!')
                return
        except:
            pass
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass
        bot.answer_callback_query(call.id)
        return
    if d.startswith('grp_num_'):
        try:
            rest = d[len('grp_num_'):]
            last_us = rest.rfind('_')
            owner_uid = int(rest[:last_us])
            cid = int(rest[last_us + 1:])
        except:
            bot.answer_callback_query(call.id)
            return
        if uid != owner_uid:
            bot.answer_callback_query(call.id, ' Sirf /start karne wala use kar sakta hai!')
            return
        if not is_feature_enabled('number'):
            bot.answer_callback_query(call.id, ' Feature OFF!')
            return
        bot.answer_callback_query(call.id)
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass
        ask = bot.send_message(cid, f"<blockquote>📱 <b>ɴᴜᴍʙᴇʀ ɪɴꜰᴏ</b>\n\n<a href='tg://user?id={uid}'><b>{fname}</b></a> — number bhejo:\n<i>Example: 9876543210</i>\n\n⚡ @notCoder2006</blockquote>", parse_mode='HTML')
        user_state[uid] = {'state': S_NUM, 'chat_id': cid, 'ask_id': ask.message_id, 'group': True, 'requester': uid}
        return
    if d.startswith('grp_insta_'):
        try:
            rest = d[len('grp_insta_'):]
            last_us = rest.rfind('_')
            owner_uid = int(rest[:last_us])
            cid = int(rest[last_us + 1:])
        except:
            bot.answer_callback_query(call.id)
            return
        if uid != owner_uid:
            bot.answer_callback_query(call.id, ' Sirf /start karne wala use kar sakta hai!')
            return
        if not False:
            bot.answer_callback_query(call.id, ' Feature OFF!')
            return
        bot.answer_callback_query(call.id)
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass
        ask = bot.send_message(cid, f"<blockquote>📸 <b></b>\n\n<a href='tg://user?id={uid}'><b>{fname}</b></a> — Instagram @username bhejo:\n<i>Example: @cristiano</i>\n\n⚡ @notCoder2006</blockquote>", parse_mode='HTML')
        user_state[uid] = {'state': S_INSTA, 'chat_id': cid, 'ask_id': ask.message_id, 'group': True, 'requester': uid}
        return
    if d.startswith('grp_bomb_'):
        try:
            rest = d[len('grp_bomb_'):]
            last_us = rest.rfind('_')
            owner_uid = int(rest[:last_us])
            cid = int(rest[last_us + 1:])
        except:
            bot.answer_callback_query(call.id)
            return
        if uid != owner_uid:
            bot.answer_callback_query(call.id, ' Sirf /start karne wala use kar sakta hai!')
            return
        if not False:
            bot.answer_callback_query(call.id, ' Feature OFF!')
            return
        bot.answer_callback_query(call.id)
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass
        ask = bot.send_message(cid, f"<blockquote>💣 <b>ʙᴏᴍʙᴇʀ</b>\n\n<a href='tg://user?id={uid}'><b>{fname}</b></a> — 10-digit number bhejo:\n<i>Example: 9876543210</i>\n\n⚡ @notCoder2006</blockquote>", parse_mode='HTML')
        user_state[uid] = {'state': S_BOMB, 'chat_id': cid, 'ask_id': ask.message_id, 'group': True, 'requester': uid}
        return
    if d.startswith('grp_usr_'):
        try:
            rest = d[len('grp_usr_'):]
            last_us = rest.rfind('_')
            owner_uid = int(rest[:last_us])
            cid = int(rest[last_us + 1:])
        except:
            bot.answer_callback_query(call.id)
            return
        if uid != owner_uid:
            bot.answer_callback_query(call.id, ' Sirf /start karne wala use kar sakta hai!')
            return
        if not is_feature_enabled('tgid'):
            bot.answer_callback_query(call.id, ' Feature OFF!')
            return
        bot.answer_callback_query(call.id)
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass
        ask = bot.send_message(cid, f"<blockquote>🆔 <b>ᴛɢ ɪᴅ ɪɴꜰᴏ</b>\n\n<a href='tg://user?id={uid}'><b>{fname}</b></a> — TG ID bhejo:\n<i>Example: 123456789</i>\n\n⚡ @notCoder2006</blockquote>", parse_mode='HTML')
        user_state[uid] = {'state': S_TID, 'chat_id': cid, 'ask_id': ask.message_id, 'group': True, 'requester': uid}
        return
    if d.startswith('grp_spn_'):
        bot.answer_callback_query(call.id)
        try:
            rest = d[len('grp_spn_'):]
            last_us = rest.rfind('_')
            cid = int(rest[last_us + 1:])
        except:
            return
        user_obj_spn = get_user(uid)
        if not user_obj_spn:
            add_user(uid, uname_tg, fname)
            user_obj_spn = get_user(uid)
        if not check_channel(uid):
            mk_fj = get_channels_keyboard(uid)
            if mk_fj:
                bot.send_message(uid, format_force_join_msg(), reply_markup=mk_fj, parse_mode='HTML')
                return
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass
        threading.Thread(target=_do_group_spin, args=(uid, fname, uname_tg, cid), daemon=True).start()
        return
    if d.startswith('grp_cho_'):
        try:
            rest = d[len('grp_cho_'):]
            last_us = rest.rfind('_')
            owner_uid = int(rest[:last_us])
            cid = int(rest[last_us + 1:])
        except:
            bot.answer_callback_query(call.id)
            return
        if uid != owner_uid:
            bot.answer_callback_query(call.id, ' Sirf /start karne wala use kar sakta hai!')
            return
        bot.answer_callback_query(call.id)
        try:
            bn3 = _get_bot_username()
        except:
            bn3 = '𝙽𝚘𝚝 𝙲𝚘𝚍𝚎𝚛_bot'
        dm_url = f'https://t.me/{bn3}?start=dm_selectuser'
        try:
            bot.send_message(uid, '<blockquote> <b>ѕᴇʟᴇᴄᴛ ᴜѕᴇʀ</b>\nNeeche button dabao aur user select karo:</blockquote>', reply_markup=kb_select_user(), parse_mode='HTML')
        except:
            pass
        mk_dm = InlineKeyboardMarkup()
        mk_dm.add(_IKB('Open in DM', style='primary', url=dm_url))
        bot.send_message(cid, '<blockquote>DM check karo! @notCoder2006</blockquote>', reply_markup=mk_dm, parse_mode='HTML')
        return
    if d.startswith('grp_') and is_admin(uid):
        if d.startswith('grp_pg_'):
            pg = int(d.split('grp_pg_')[1])
            try:
                bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=kb_groups_inline(pg))
            except:
                pass
            bot.answer_callback_query(call.id)
            return
        if d == 'grp_back_list':
            try:
                bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=kb_groups_inline())
            except:
                pass
            bot.answer_callback_query(call.id)
            return
        if d == 'grp_back_menu':
            bot.answer_callback_query(call.id)
            bot.send_message(uid, '<blockquote><b>Admin Panel P2</b></blockquote>', reply_markup=kb_admin_p2(), parse_mode='HTML')
            return
        if d.startswith('grp_sel_'):
            gid2 = int(d.split('grp_sel_')[1])
            refresh_group_msg(call.message.chat.id, call.message.message_id, gid2)
            bot.answer_callback_query(call.id)
            return
        if d.startswith('grp_unl_'):
            gid2 = int(d.split('grp_unl_')[1])
            toggle_group_unlimited(gid2)
            refresh_group_msg(call.message.chat.id, call.message.message_id, gid2)
            bot.answer_callback_query(call.id, ' Updated')
            return
        if d.startswith('grp_blk_'):
            gid2 = int(d.split('grp_blk_')[1])
            toggle_group_block(gid2)
            refresh_group_msg(call.message.chat.id, call.message.message_id, gid2)
            bot.answer_callback_query(call.id, ' Updated')
            return
        if d.startswith('grp_mute_'):
            gid2 = int(d.split('grp_mute_')[1])
            toggle_group_mute(gid2)
            refresh_group_msg(call.message.chat.id, call.message.message_id, gid2)
            bot.answer_callback_query(call.id, ' Updated')
            return
        if d.startswith('grp_info_'):
            gid2 = int(d.split('grp_info_')[1])
            refresh_group_msg(call.message.chat.id, call.message.message_id, gid2)
            bot.answer_callback_query(call.id)
            return
    if d == 'grpctrl_back' and is_admin(uid):
        bot.answer_callback_query(call.id)
        try:
            bot.edit_message_reply_markup(call.message.chat.id,call.message.message_id,reply_markup=kb_group_mgmt())
        except Exception:
            bot.send_message(uid,'<blockquote><b>Group Management</b></blockquote>',reply_markup=kb_group_mgmt(),parse_mode='HTML')
        return
    if d.startswith('grpctrl_') and is_admin(uid):
        bot.answer_callback_query(call.id)
        groups = get_all_groups()
        if d.startswith('grpctrl_tog_'):
            parts_tog = d.split('_')
            try:
                gid_tog = int(parts_tog[2])
                page_tog = int(parts_tog[3]) if len(parts_tog) > 3 else 1
            except:
                gid_tog = 0
                page_tog = 1
            if gid_tog:
                g_tog = get_group(gid_tog)
                if g_tog:
                    new_state = toggle_group_unlimited(gid_tog)
                    status_txt = ' UNLIMITED' if new_state else ' LIMITED'
                    title_tog = next((t for gi, t in groups if gi == gid_tog), str(gid_tog))
                    bot.answer_callback_query(call.id, f'{status_txt} — {title_tog[:20]}', show_alert=False)
            _send_group_control_panel(call.message.chat.id, call.message.message_id, page_tog)
            return
        if d.startswith('grpctrl_pg_'):
            try:
                page_nav = int(d.split('_')[2])
            except:
                page_nav = 1
            _send_group_control_panel(call.message.chat.id, call.message.message_id, page_nav)
            return
        if d == 'grpctrl_all_unl':
            count = 0
            for gid2, _ in groups:
                g2 = get_group(gid2)
                if g2 and safe_g(g2, 5) != 1:
                    toggle_group_unlimited(gid2)
                    count += 1
            bot.answer_callback_query(call.id, f'✅ {count} groups → UNLIMITED')
            _send_group_control_panel(call.message.chat.id, call.message.message_id)
            return
        if d == 'grpctrl_all_lim':
            count = 0
            for gid2, _ in groups:
                g2 = get_group(gid2)
                if g2 and safe_g(g2, 5) == 1:
                    toggle_group_unlimited(gid2)
                    count += 1
            bot.answer_callback_query(call.id, f'🔴 {count} groups → LIMITED')
            _send_group_control_panel(call.message.chat.id, call.message.message_id)
            return
    if d == 'confirm_revoke_premium' and is_admin(uid):
        bot.answer_callback_query(call.id, ' Revoking...')
        try:
            prem_users = c.execute('SELECT user_id FROM users WHERE is_premium=1').fetchall()
            for puid, in prem_users:
                c.execute('UPDATE users SET is_premium=0,premium_until=NULL,credits=? WHERE user_id=?', (FREE_CREDITS, puid))
            c.execute('UPDATE users SET credits=? WHERE is_premium=0', (FREE_CREDITS,))
            c.execute('DELETE FROM redeemed_premium')
            c.execute('DELETE FROM premium_codes')
            c.execute('DELETE FROM redeemed_users')
            c.execute('DELETE FROM redeem_codes')
            conn.commit()
            count = len(prem_users)
            try:
                bot.edit_message_text(f'<blockquote>💀 <b>REVOKE DONE!</b>\n💎 {count} users premium removed.\n⚡ @notCoder2006</blockquote>', call.message.chat.id, call.message.message_id, parse_mode='HTML')
            except:
                pass
        except Exception as e:
            try:
                bot.edit_message_text(f'<blockquote>❌ {_safe_err(e)}</blockquote>', call.message.chat.id, call.message.message_id, parse_mode='HTML')
            except:
                pass
        return
    if d == 'cancel_revoke_premium':
        bot.answer_callback_query(call.id, ' Cancelled')
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception:
            pass
        return
    if d == 'confirm_clear' and is_admin(uid):
        bot.answer_callback_query(call.id)
        c.execute('DELETE FROM search_history')
        conn.commit()
        try:
            bot.edit_message_text('<blockquote> History cleared!</blockquote>', call.message.chat.id, call.message.message_id, parse_mode='HTML')
        except Exception:
            pass
        return
    if d == 'cancel_clear':
        bot.answer_callback_query(call.id, ' Cancelled')
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception:
            pass
        return
    bot.answer_callback_query(call.id)

def _register_bot_group_from_status(update):
    try:
        chat = getattr(update, 'chat', None)
        new_m = getattr(update, 'new_chat_member', None)
        if not chat or not new_m or getattr(chat, 'type', '') not in ('group', 'supergroup'):
            return
        new_status = getattr(new_m, 'status', '')
        if new_status in ('member', 'administrator'):
            add_group_to_db(chat.id, chat.title or 'Unknown')
            print(f'[GROUP_REGISTER] {chat.id} / {chat.title or "Unknown"}')
    except Exception as e:
        print(f'[GROUP_REGISTER] {e}')

if hasattr(bot, 'my_chat_member_handler'):
    @bot.my_chat_member_handler()
    def h_my_chat_member_updated(update):
        _register_bot_group_from_status(update)

@bot.chat_member_handler()
def h_chat_member_updated(update):
    """Handle hidden joins and hidden leaves via ChatMemberUpdated"""
    try:
        if not update or not update.new_chat_member:
            return
        new_m = update.new_chat_member
        old_m = update.old_chat_member
        cid = update.chat.id
        chat_type = getattr(update.chat, 'type', '')
        # Force-join channel membership updates must not trigger group welcome/leave logic.
        if chat_type == 'channel':
            return
        chat_title = update.chat.title or 'Group'
        old_status = old_m.status if old_m else 'left'
        new_status = new_m.status
        mb = new_m.user
        if not mb or mb.is_bot:
            return
        if new_status in ('member', 'administrator', 'creator', 'restricted') and chat_type in ('group', 'supergroup'):
            add_group_to_db(cid, chat_title)
        if old_status in ('member', 'administrator', 'creator', 'restricted') and new_status in ('left', 'kicked'):
            try:
                _bye_val = get_group_bye(cid)
                if not _bye_val:
                    return
            except:
                return
            try:
                fname = mb.first_name or 'Hidden User'
                lname = mb.last_name or ''
                full_name = (fname + ' ' + lname).strip()
                uname = '@' + mb.username if mb.username else 'ʜɪᴅᴅᴇɴ ᴜꜱᴇʀ'
                now = _now_ist()
                try:
                    mem_count = bot.get_chat_members_count(cid)
                except:
                    mem_count = '?'

                def _te(*args, **kwargs): return ""
                _LOOP10 = _te('5465629669829128119') * 10
                left_txt = f"<blockquote>{_te('4958830950604604428')} <a href='tg://user?id={mb.id}'><b>{full_name}</b></a> ʜᴀꜱ ʟᴇꜰᴛ ᴛʜᴇ ɢʀᴏᴜᴩ 😢\n{_LOOP10}\n\n{_te('4956461073550017373')} ɴᴀᴍᴇ  : <b>{full_name}</b>\n{_te('6147422674000808494')} ɪᴅ    : <code>{mb.id}</code>\n{_te('4958636483075376288')} ᴜꜱᴇʀ  : {uname}\n\n{_te('4958724224962265918')} ɢʀᴏᴜᴩ : <b>{chat_title}</b>\n{_te('4958472587123360612')} ᴍᴇᴍʙᴇʀꜱ : <b>{mem_count}</b>\n{_te('4956525562483967357')} ᴛɪᴍᴇ  : {now}\n\n{_LOOP10}\n{_te('4958900559139570572')} ᴅᴇᴠᴇʟᴏᴩᴇʀ : @notCoder2006</blockquote>"
                bot.send_message(cid, left_txt, parse_mode='HTML')
            except Exception as _hl_e:
                print(f'[HIDDEN_LEFT] {_hl_e}')
            return
        if old_status in ('left', 'kicked') and new_status in ('member', 'administrator', 'creator', 'restricted'):
            if _join_already_welcomed(cid, mb.id):
                return
            try:
                wel_on, rules = get_group_welcome(cid)
                if not wel_on:
                    return
            except:
                return
            try:
                fname = mb.first_name or 'User'
                lname = mb.last_name or ''
                full_name = (fname + ' ' + lname).strip()
                uname = '@' + mb.username if mb.username else 'No Username'
                tgid = mb.id
                now = _now_ist()
                try:
                    mem_count = bot.get_chat_members_count(cid)
                except:
                    mem_count = '?'
                pic = _fetch_pfp_by_id(str(tgid))

                def _te(*args, **kwargs): return ""
                uname_disp = uname if uname != 'No Username' else f'<code>{tgid}</code>'
                gwimg, gwvid, gwvlist, gwstk = get_group_welcome_media(cid)
                try:
                    c.execute('SELECT welcome_text FROM group_welcome_settings WHERE group_id=?', (cid,))
                    gwtext_row = c.fetchone()
                    gwtext = gwtext_row[0] if gwtext_row and gwtext_row[0] else None
                except:
                    gwtext = None
                _LOOP10 = _te('5465629669829128119') * 10
                _dev_footer = f"{_te('4958900559139570572')} ᴅᴇᴠᴇʟᴏᴩᴇʀ : @notCoder2006"
                if rules:
                    _rules_lines = '\n'.join((f'• {r.strip()}' for r in rules.splitlines() if r.strip()))
                else:
                    _rules_lines = f"{_te('4958636483075376288')} ɴᴏ ꜱᴘᴀᴍ\n{_te('4958472587123360612')} ɴᴏ ᴀʙᴜꜱᴇ\n{_te('4956525562483967357')} ʀᴇꜱᴩᴇᴄᴛ ᴇᴠᴇʀʏᴏɴᴇ"
                welcome_txt = f"<blockquote>{_te('4958830950604604428')} ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴛʜᴇ <b>{chat_title}</b> !!\n{_LOOP10}\n{_te('4956461073550017373')}{_te('4958469026595472714')} ʜᴇʟʟᴏ 殺┋ <a href='tg://user?id={tgid}'><b>{full_name}</b></a> !!\n\n{_te('6147422674000808494')}  /help — ꜱᴀʀᴇ ᴄᴏᴍᴍᴀɴᴅ ᴅᴇᴋʜᴏ\n\n{_te('4958724224962265918')} ʀᴜʟᴇꜱ:\n{_rules_lines}\n\n{_LOOP10}\n{_dev_footer}</blockquote>"
                if gwtext:
                    welcome_txt = gwtext.replace('{name}', full_name).replace('{id}', str(tgid)).replace('{username}', uname).replace('{group}', chat_title)
                if gwstk:
                    try:
                        bot.send_sticker(cid, gwstk)
                    except:
                        pass
                sent2 = False
                if gwvlist:
                    fid2 = get_next_group_video(cid)
                    if fid2:
                        try:
                            bot.send_video(cid, fid2, caption=welcome_txt, parse_mode='HTML')
                            sent2 = True
                        except:
                            pass
                if not sent2 and gwvid:
                    sent2 = _send_saved_group_media(cid, gwvid, 'video', welcome_txt)
                if not sent2 and gwimg:
                    sent2 = _send_saved_group_media(cid, gwimg, 'photo', welcome_txt)
                if not sent2 and pic:
                    try:
                        bot.send_photo(cid, pic, caption=welcome_txt, parse_mode='HTML', message_effect_id='5046509860389126442')
                        sent2 = True
                    except:
                        pass
                if not sent2:
                    try:
                        bot.send_message(cid, welcome_txt, parse_mode='HTML', message_effect_id='5046509860389126442')
                    except:
                        pass
            except Exception as _hj_e:
                print(f'[HIDDEN_JOIN] {_hj_e}')
    except Exception as _cmu_e:
        print(f'[CHAT_MEMBER_UPD] {_cmu_e}')


# Recovered runtime helpers (kept outside the removed legacy systems).
def get_user(uid):
    if uid in _user_cache:
        return _user_cache[uid]
    c.execute('SELECT * FROM users WHERE user_id=?', (uid,))
    row = c.fetchone()
    _user_cache[uid] = row
    return row

def add_user(uid, uname, fname, ref=None):
    _user_cache.pop(uid, None)
    d = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        result = c.execute('INSERT OR IGNORE INTO users(user_id,username,first_name,join_date,referrer,credits,first_time) VALUES(?,?,?,?,?,?,1)', (uid, uname, fname, d, ref, FREE_CREDITS))
        is_new = c.rowcount > 0 if hasattr(c, '_cur') else True
        if ref and ref != uid and is_new:
            c.execute('INSERT INTO referrals(referrer,referred,date) VALUES(?,?,?)', (ref, uid, d))
            c.execute('UPDATE users SET credits=COALESCE(credits,0)+? WHERE user_id=?', (get_referral_bonus(), ref))
            try:
                _ref_uname = f'@{uname}' if uname else fname or f'User {uid}'
                _ref_credits_now = c.execute('SELECT credits FROM users WHERE user_id=?', (ref,)).fetchone()
                _ref_cr_val = _ref_credits_now[0] or 0 if _ref_credits_now else 2
                _ref_cnt = c.execute('SELECT COUNT(*) FROM referrals WHERE referrer=?', (ref,)).fetchone()
                _ref_cnt_val = _ref_cnt[0] or 0 if _ref_cnt else 1

                def _rte(eid, fb='⭐'):
                    return f"{fb}"
                _e_party = _rte('6134194260628479379', '')
                _e_ok1 = _rte('5980930633298350051', '')
                _e_loop = _rte('5465270065102334742', '')
                _e_ok2 = _rte('6111827380915934490', '')
                _e_purse = _rte('6105124659248765862', '')
                _e_folder = _rte('6104913737699828239', '')
                _L8 = _e_loop * 8
                _bonus = get_referral_bonus()
                _notif = f"<blockquote>{_e_party}  Nᴇᴡ Vᴇʀɪꜰɪᴇᴅ Rᴇꜰᴇʀʀᴀʟ! {_e_ok1}\n{_L8}\n{_e_ok2} {_ref_uname} ᴊᴏɪɴᴇᴅ ᴀɴᴅ ᴠᴇʀɪꜰɪᴇᴅ!\n{_e_purse} ʏᴏᴜ'ᴠᴇ ᴇᴀʀɴᴇᴅ +{_bonus} ᴘᴏɪɴᴛ.\n{_e_folder} ᴛᴏᴛᴀʟ ᴠᴇʀɪꜰɪᴇᴅ ʀᴇꜰᴇʀʀᴀʟꜱ: {_ref_cnt_val}\n{_L8}</blockquote>"
                bot.send_message(ref, _notif, parse_mode='HTML')
            except:
                pass
        conn.commit()
        if is_new:
            try:
                try:
                    bn = _get_bot_username()
                except:
                    bn = '𝙽𝚘𝚝 𝙲𝚘𝚍𝚎𝚛_bot'
                log_token_activity(uid, fname, uname, FREE_CREDITS, FREE_CREDITS, 'New Join', bn)
            except:
                pass
        return True
    except:
        return False

def update_user(uid, **kw):
    _user_cache.pop(uid, None)
    for k, v in kw.items():
        c.execute(f'UPDATE users SET {k}=? WHERE user_id=?', (v, uid))
    conn.commit()

def get_credits(uid):
    if is_admin(uid):
        return '∞'
    c.execute('SELECT credits,is_premium,premium_until FROM users WHERE user_id=?', (uid,))
    r = c.fetchone()
    if not r:
        return 0
    if r[1] == 1 and r[2]:
        try:
            if datetime.strptime(r[2], '%Y-%m-%d %H:%M:%S') > datetime.now():
                return '∞'
        except:
            pass
    return r[0] if r[0] is not None else 0

def deduct_credit(uid, cost=1, context='bot'):
    if is_admin(uid):
        return True
    if context and str(context).lstrip('-').isdigit():
        _grp_ctx = get_group(int(context))
        if _grp_ctx and safe_g(_grp_ctx, 5) == 1:
            return True
    _user_cache.pop(uid, None)
    c.execute('SELECT credits,is_premium,premium_until FROM users WHERE user_id=?', (uid,))
    u = c.fetchone()
    if not u:
        return False
    if u[1] == 1 and u[2]:
        try:
            if datetime.strptime(u[2], '%Y-%m-%d %H:%M:%S') > datetime.now():
                return True
        except:
            pass
    if u[0] >= cost:
        c.execute('UPDATE users SET credits=credits-? WHERE user_id=?', (cost, uid))
        conn.commit()
        _user_cache.pop(uid, None)
        return True
    return False

def refund_credit(uid, cost=1):
    if is_admin(uid):
        return
    c.execute('UPDATE users SET credits=credits+? WHERE user_id=?', (cost, uid))
    conn.commit()
    _user_cache.pop(uid, None)

def get_referral_count(uid):
    c.execute('SELECT COUNT(*) FROM referrals WHERE referrer=?', (uid,))
    return c.fetchone()[0] or 0

def can_claim_daily(uid):
    if is_admin(uid):
        return True
    today = datetime.now().strftime('%Y-%m-%d')
    c.execute('SELECT COUNT(*) FROM daily_claims WHERE user_id=? AND claim_date=?', (uid, today))
    return c.fetchone()[0] == 0

def get_group_welcome(gid):
    c.execute('SELECT welcome_on, group_rules FROM group_welcome_settings WHERE group_id=?', (gid,))
    r = c.fetchone()
    if r:
        return (r[0], r[1] or '')
    c.execute("INSERT OR IGNORE INTO group_welcome_settings(group_id,welcome_on,group_rules,updated_date) VALUES(?,1,'',?)", (gid, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    conn.commit()
    return (1, '')

def get_group_bye(gid):
    """Returns bye_on status (1=on, 0=off). Default ON."""
    try:
        c.execute('SELECT bye_on FROM group_welcome_settings WHERE group_id=?', (gid,))
        r = c.fetchone()
        if r:
            return r[0] if r[0] is not None else 1
    except:
        pass
    return 1

def set_group_bye_on(gid, val):
    try:
        c.execute("INSERT OR IGNORE INTO group_welcome_settings(group_id,welcome_on,group_rules,updated_date) VALUES(?,1,'',?)", (gid, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        c.execute('UPDATE group_welcome_settings SET bye_on=?,updated_date=? WHERE group_id=?', (val, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), gid))
        conn.commit()
    except Exception as e:
        print(f'[BYE_SET] {e}')

def set_group_welcome_on(gid, val):
    """welcome_on toggle karo — baaki columns (video/image/sticker) preserve karo"""
    try:
        c.execute("INSERT OR IGNORE INTO group_welcome_settings(group_id,welcome_on,group_rules,updated_date) VALUES(?,1,'',?)", (gid, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        c.execute('UPDATE group_welcome_settings SET welcome_on=?,updated_date=? WHERE group_id=?', (val, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), gid))
        conn.commit()
    except Exception as e:
        print(f'[SET_WEL_ON] {e}')

def set_group_rules(gid, rules):
    try:
        c.execute("INSERT OR IGNORE INTO group_welcome_settings(group_id,welcome_on,group_rules,updated_date) VALUES(?,1,'',?)", (gid, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        c.execute('UPDATE group_welcome_settings SET group_rules=?,updated_date=? WHERE group_id=?', (rules, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), gid))
        conn.commit()
    except Exception as e:
        print(f'[SET_RULES] {e}')

def get_group_welcome_media(gid):
    """Return (image_path, video_path, video_list_json, sticker_id) for group welcome"""
    try:
        c.execute('SELECT welcome_image,welcome_video,video_list,group_sticker FROM group_welcome_settings WHERE group_id=?', (gid,))
        r = c.fetchone()
        if r:
            return (r[0], r[1], r[2], r[3] if len(r) > 3 else None)
    except:
        pass
    return (None, None, None, None)

def set_group_welcome_image(gid, path):
    c.execute("INSERT OR IGNORE INTO group_welcome_settings(group_id,welcome_on,group_rules,updated_date) VALUES(?,1,'',?)", (gid, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    c.execute('UPDATE group_welcome_settings SET welcome_image=?,updated_date=? WHERE group_id=?', (path, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), gid))
    conn.commit()

def set_group_welcome_video(gid, path):
    c.execute("INSERT OR IGNORE INTO group_welcome_settings(group_id,welcome_on,group_rules,updated_date) VALUES(?,1,'',?)", (gid, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    c.execute('UPDATE group_welcome_settings SET welcome_video=?,updated_date=? WHERE group_id=?', (path, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), gid))
    conn.commit()

def set_group_welcome_video_list(gid, lst_json):
    c.execute("INSERT OR IGNORE INTO group_welcome_settings(group_id,welcome_on,group_rules,updated_date) VALUES(?,1,'',?)", (gid, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    c.execute('UPDATE group_welcome_settings SET video_list=?,updated_date=? WHERE group_id=?', (lst_json, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), gid))
    conn.commit()

def set_group_welcome_sticker(gid, stk_id):
    c.execute("INSERT OR IGNORE INTO group_welcome_settings(group_id,welcome_on,group_rules,updated_date) VALUES(?,1,'',?)", (gid, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    c.execute('UPDATE group_welcome_settings SET group_sticker=?,updated_date=? WHERE group_id=?', (stk_id, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), gid))
    conn.commit()

def get_next_group_video(gid):
    """Round-robin se next video file_id return karo from video_list"""
    try:
        c.execute('SELECT video_list FROM group_welcome_settings WHERE group_id=?', (gid,))
        r = c.fetchone()
        if not r or not r[0]:
            return None
        lst = json.loads(r[0])
        if not lst:
            return None
        idx = _grp_video_idx.get(gid, 0) % len(lst)
        _grp_video_idx[gid] = idx + 1
        return lst[idx]
    except:
        return None

def format_force_join_msg():
    """Premium force-join message"""

    def te(eid, fb='⭐'):
        return f"{fb}"
    L = te('5465270065102334742', '') * 10
    _zwj = '\u200d'
    return f"""<blockquote>{L}\n{te('6158873829906063765', '')} ᴊᴏɪɴ ʀᴇǫᴜɪʀᴇᴅ! {te('6158690786989844701', '')}\n{L}\n\n{te('6133910874391322379', '')} ʙᴏᴛ ᴜꜱᴇ ᴋᴀʀɴᴇ ᴋᴇ ʟɪʏᴇ\n\n{te('6158903873202297860', '')} ɴᴇᴇᴄʜᴇ ᴅɪʏᴇ ɢᴀʏᴇ ꜱᴀᴀʀᴇ ᴄʜᴀɴɴᴇʟꜱ ᴊᴏɪɴ ᴋᴀʀɴᴀ ᴢᴀʀᴏᴏʀɪ ʜᴀɪ.\n\n{te('6071022434234930063', '')} ᴊᴏɪɴ ᴋᴀʀɴᴇ ᴋᴇ ʙᴀᴀᴅ ᴠᴇʀɪꜰʏ ᴅᴀʙᴀᴏ.\n\n{L}\n{te('4958900559139570572', _zwj)} ᴏᴡɴᴇʀ : <a href="https://t.me/notCoder2006">𝙽𝚘𝚝 𝙲𝚘𝚍𝚎𝚛</a>\n</blockquote>"""

def _ensure_join_req_table():
    try:
        c.execute("""CREATE TABLE IF NOT EXISTS join_requests(
            user_id INTEGER,
            chat_id INTEGER,
            requested_at TEXT,
            PRIMARY KEY(user_id, chat_id)
        )""")
        conn.commit()
    except Exception as e:
        print(f'[JOIN_REQ_TABLE] {e}')

def _track_join_request(user_id, chat_id):
    try:
        uid = int(user_id)
        cid = int(chat_id)
        _ensure_join_req_table()
        c.execute(
            'INSERT OR REPLACE INTO join_requests(user_id,chat_id,requested_at) VALUES(?,?,?)',
            (uid, cid, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        )
        conn.commit()
        _channel_check_cache.pop(uid, None)
    except Exception as e:
        print(f'[TRACK_JOIN] {e}')

def _clear_join_request(user_id, chat_id):
    try:
        _ensure_join_req_table()
        c.execute(
            'DELETE FROM join_requests WHERE user_id=? AND chat_id=?',
            (int(user_id), int(chat_id))
        )
        conn.commit()
    except Exception as e:
        print(f'[CLEAR_JOIN_REQ] {e}')

def _has_join_request(user_id, chat_id):
    try:
        _ensure_join_req_table()
        resolved = _resolve_chat_id(chat_id) if not str(chat_id).lstrip('-').isdigit() else int(chat_id)
        if resolved is None:
            return False
        return bool(c.execute(
            'SELECT 1 FROM join_requests WHERE user_id=? AND chat_id=?',
            (int(user_id), int(resolved))
        ).fetchone())
    except Exception:
        return False

def _user_satisfied_channel(uid, cid_str):
    """Check real Telegram membership; never trust a stale join-request record."""
    cid_text = str(cid_str).strip()
    resolved = _resolve_chat_id(cid_text)
    if resolved is None:
        print(f'[FJ_CHECK] Could not resolve force-join chat: {cid_text}')
        return False
    try:
        mem = bot.get_chat_member(resolved, int(uid))
        status = getattr(mem, 'status', 'left')
        # A real member/admin/owner is satisfied. Restricted is still a member.
        if status in ('member', 'administrator', 'creator', 'restricted'):
            _clear_join_request(uid, resolved)
            return True
        # left/kicked is definitely not satisfied; remove stale approval/request state.
        if status in ('left', 'kicked'):
            _clear_join_request(uid, resolved)
            return False
        return False
    except Exception as e:
        print(f'[FJ_CHECK] get_chat_member failed for {resolved}: {e}')
        # Pending join requests are not treated as a completed join. This prevents
        # stale requests from permanently bypassing or trapping force-join checks.
        return False

def check_channel(uid):
    """Return True only when the user is actually in every active force-join channel."""
    chs = get_force_join_channels()
    if not chs:
        return True
    all_ok = all(_user_satisfied_channel(uid, str(entry[0])) for entry in chs)
    try:
        c.execute(
            'UPDATE users SET joined_channel=? WHERE user_id=?',
            (1 if all_ok else 0, int(uid))
        )
        conn.commit()
    except Exception:
        pass
    if all_ok:
        _channel_check_cache.pop(uid, None)
    return all_ok

@bot.chat_join_request_handler()
def h_chat_join_request(req):
    try:
        uid = int(req.from_user.id)
        cid = int(req.chat.id)
        _track_join_request(uid, cid)
    except Exception as e:
        print(f'[JOIN_REQUEST] {e}')

try:
    _ensure_join_req_table()
except Exception:
    pass

def is_admin(uid):
    """Single source of truth: owner + active admins only. No clone/protected-user paths."""
    try:
        uid=int(uid)
    except Exception:
        return False
    if uid == OWNER_ID:
        return True
    if uid in _admin_cache:
        return bool(_admin_cache[uid])
    try:
        ok=bool(c.execute('SELECT 1 FROM admins WHERE user_id=? AND is_active=1 LIMIT 1',(uid,)).fetchone())
    except Exception:
        ok=False
    _admin_cache[uid]=ok
    return ok


def is_feature_enabled(fn):
    """Feature switches are persisted, but the Admin UI exposes only Number Info."""
    if fn in _feature_cache:
        return _feature_cache[fn]
    try:
        with _db_lock:
            row=_orig_conn.execute('SELECT is_enabled FROM feature_toggles WHERE feature_name=?',(fn,)).fetchone()
        result=(row[0] == 1) if row else True
    except Exception:
        result=True
    _feature_cache[fn]=result
    return result


def toggle_feature(fn, by):
    if fn != 'number':
        raise ValueError('Only Number Info can be toggled from the Admin Panel.')
    with _db_lock:
        row=_orig_conn.execute('SELECT is_enabled FROM feature_toggles WHERE feature_name=?',('number',)).fetchone()
        nv=0 if row and row[0] == 1 else 1
        _orig_conn.execute("INSERT OR IGNORE INTO feature_toggles(feature_name,is_enabled,updated_by,updated_date) VALUES('number',?,?,?)",(nv,by,datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        _orig_conn.execute("UPDATE feature_toggles SET is_enabled=?,updated_by=?,updated_date=? WHERE feature_name='number'",(nv,by,datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        _orig_conn.commit()
    _feature_cache['number']=(nv==1)
    return nv==1


def get_all_feature_states():
    with _db_lock:
        return _orig_conn.execute("SELECT feature_name,is_enabled FROM feature_toggles WHERE feature_name='number' ORDER BY feature_name").fetchall()


def _cleanup_feature_toggles():
    try:
        with _db_lock:
            _orig_conn.execute("DELETE FROM feature_toggles WHERE feature_name <> 'number'")
            _orig_conn.execute("INSERT OR IGNORE INTO feature_toggles(feature_name,is_enabled,updated_by,updated_date) VALUES('number',1,?,?)",(OWNER_ID,datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            _orig_conn.commit()
        _feature_cache.pop('number',None)
    except Exception as _feature_cleanup_e:
        print(f'[FEATURE_CLEANUP] {_feature_cleanup_e}')

_cleanup_feature_toggles()


def _fj_normalize(cid):
    s=str(cid).strip().lower()
    if 't.me/' in s:
        s=s.split('t.me/',1)[1].strip('/')
    if s.startswith('@'):
        s=s[1:]
    return s

_chat_id_cache={}
def _resolve_chat_id(cid_str):
    s=str(cid_str).strip()
    if s.lstrip('-').isdigit():
        return int(s)
    if s.startswith('https://t.me/'):
        tail=s.split('https://t.me/',1)[1].strip('/')
        if tail.startswith(('+','joinchat/')):
            return None
        s='@'+tail
    if not s.startswith('@'):
        s='@'+s
    key=s.lower()
    if key in _chat_id_cache:
        return _chat_id_cache[key]
    try:
        ch=bot.get_chat(s)
        _chat_id_cache[key]=ch.id
        return ch.id
    except Exception:
        return None


def get_force_join_channels():
    """Force-join disabled: this build runs without requiring any channel/group join."""
    return []
    seen = set()
    rows = []
    for chat_id, title, url in FORCE_JOIN_DEFAULT_CHANNELS:
        nk = _fj_normalize(chat_id)
        if nk not in seen:
            rows.append((chat_id, title, url))
            seen.add(nk)
    try:
        raw_rows = c.execute(
            'SELECT chat_id,chat_title,chat_url FROM force_join_channels WHERE is_active=1 ORDER BY id'
        ).fetchall()
    except Exception:
        raw_rows = []
    for r in raw_rows:
        nk = _fj_normalize(r[0])
        if nk not in seen:
            rows.append((r[0], r[1], r[2]))
            seen.add(nk)
    return rows


def _CL_TOP():
    return _PREM_EMOJI * 10

def _CL_BOT():
    return _PREM_EMOJI * 10

def _SEP():
    return '━━━━━━━━━━━━━━━━━━━━━━━━━━'

def _orig_credit():
    return '\n @notCoder2006 \n'

def _credit():
    return _orig_credit()
# ======================= GLOBAL GATE: ban + maintenance (commands, buttons, callbacks) =======================
def _bg(fn, *a, **k):
    threading.Thread(target=lambda: _gate_safe(fn, *a, **k), daemon=True).start()

def _gate_safe(fn, *a, **k):
    try:
        fn(*a, **k)
    except Exception as e:
        print(f'[GATE] {e}')

def _gate_reply(uid, chat_id, is_private, text, reply_to=None):
    if is_private:
        bot.send_message(chat_id, text, parse_mode='HTML')
    elif reply_to:
        bot.send_message(chat_id, text, parse_mode='HTML', reply_to_message_id=reply_to)

def _update_allowed(u):
    """False => update drop (banned / maintenance). Admin & owner hamesha allowed."""
    cq = getattr(u, 'callback_query', None)
    if cq is not None:
        usr = getattr(cq, 'from_user', None)
        if usr is None or is_admin(usr.id):
            return True
        if is_user_banned(usr.id):
            _bg(bot.answer_callback_query, cq.id, 'You are blocked!', show_alert=True)
            _bg(bot.send_message, usr.id, _BANNED_TEXT, parse_mode='HTML')
            return False
        if is_maintenance():
            _bg(bot.answer_callback_query, cq.id, 'Dashboard currently under maintenance, please wait.', show_alert=True)
            _bg(bot.send_message, usr.id, _maint_text(), parse_mode='HTML')
            return False
        return True
    iq = getattr(u, 'inline_query', None)
    if iq is not None:
        usr = getattr(iq, 'from_user', None)
        if usr is None or is_admin(usr.id):
            return True
        return not (is_user_banned(usr.id) or is_maintenance())
    msg = getattr(u, 'message', None)
    if msg is None:
        return True
    usr = getattr(msg, 'from_user', None)
    if usr is None or getattr(usr, 'is_bot', False) or is_admin(usr.id):
        return True
    chat = getattr(msg, 'chat', None)
    private = getattr(chat, 'type', 'private') == 'private'
    text = getattr(msg, 'text', None) or ''
    is_cmd = text.startswith('/')
    if not private and getattr(msg, 'content_type', 'text') != 'text':
        return True
    banned = is_user_banned(usr.id)
    maint = (not banned) and is_maintenance()
    if not banned and not maint:
        return True
    cid = chat.id if chat is not None else usr.id
    if banned:
        if private:
            _bg(_gate_reply, usr.id, cid, True, _BANNED_TEXT)
        return False
    if private or is_cmd:
        _bg(_gate_reply, usr.id, cid, private, _maint_text(), getattr(msg, 'message_id', None))
    return False

_orig_process_new_updates = bot.process_new_updates

def _gated_process_new_updates(updates):
    keep = []
    for u in updates:
        try:
            ok = _update_allowed(u)
        except Exception as e:
            print(f'[GATE] {e}')
            ok = True
        if ok:
            keep.append(u)
    if len(keep) != len(updates):
        # dropped updates ka offset aage badhao, warna polling wahi updates dobara layegi
        try:
            bot.last_update_id = max([getattr(bot, 'last_update_id', 0)] + [getattr(x, 'update_id', 0) for x in updates])
        except Exception:
            pass
    if keep:
        _orig_process_new_updates(keep)

bot.process_new_updates = _gated_process_new_updates




if __name__ == '__main__':
    print('╔══════════════════════════════════════════════════════════╗')
    print('║      NOT CODER INFO BOT - v1 (NUM-INFO API FIXED       ║')
    print('╠══════════════════════════════════════════════════════════╣')
    print('║═══════════════════════════════════╝')
    _cleanup_feature_toggles()
    try:
        bot.remove_webhook()
    except:
        pass
    time.sleep(0.5)
    try:
        _clear_telegram_command_menu()
    except Exception as _menu_e:
        print(f'[TG_MENU] cleanup failed: {_menu_e}')
    while True:
        try:
            print(' 𝙽𝚘𝚝 𝙲𝚘𝚍𝚎𝚛 Info Bot running...')
            bot.infinity_polling(timeout=30, long_polling_timeout=30, allowed_updates=['message', 'edited_message', 'callback_query', 'chat_member', 'my_chat_member', 'inline_query', 'chosen_inline_result', 'channel_post', 'chat_join_request'])
        except KeyboardInterrupt:
            print('\n Stopped!')
            conn.close()
            break
        except Exception as e:
            print(f'❌ Error: {_safe_err(e)}')
            time.sleep(5)
