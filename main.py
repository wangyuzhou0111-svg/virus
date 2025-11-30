import pygame
import random
import math
import json
import sys
import os

# PyInstaller 打包后资源路径处理
def resource_path(relative_path):
    """获取资源文件的绝对路径，支持 PyInstaller 打包后的环境"""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller 打包后的临时目录
        base_path = sys._MEIPASS
    else:
        # 开发环境，使用当前文件所在目录
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

# 导入画质增强模块
from graphics_enhancement import ParticleSystem, LightingSystem

# 添加Camera类
class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0
    
    def update(self, x, y):
        self.x = x
        self.y = y
    
    def apply(self, x, y):
        return x - self.x, y - self.y

# Initialize Pygame
pygame.init()

# 禁用输入法（防止中文输入法干扰游戏按键）
pygame.key.stop_text_input()

# Set up game window
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 1000
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("免疫大作战")

# 设置窗口图标（任务栏图标）
try:
    icon_image = pygame.image.load(resource_path("logo.png"))
    pygame.display.set_icon(icon_image)
except (pygame.error, FileNotFoundError):
    print("警告：无法加载 logo.png 作为窗口图标")

# 初始化中文字体
CHINESE_FONT_PATH = resource_path("STHeiti Light.ttc")
try:
    FONT_LARGE = pygame.font.Font(CHINESE_FONT_PATH, 22)
    FONT_SMALL = pygame.font.Font(CHINESE_FONT_PATH, 16)
    FONT_TINY = pygame.font.Font(CHINESE_FONT_PATH, 14)
    FONT_TITLE = pygame.font.Font(CHINESE_FONT_PATH, 48)
except:
    print("警告：无法加载中文字体，使用默认字体")
    FONT_LARGE = pygame.font.Font(None, 22)
    FONT_SMALL = pygame.font.Font(None, 16)
    FONT_TINY = pygame.font.Font(None, 14)
    FONT_TITLE = pygame.font.Font(None, 48)

# 初始化粒子系统
particle_system = ParticleSystem()
# 初始化光照系统
lighting_system = LightingSystem(WINDOW_WIDTH, WINDOW_HEIGHT)
# 初始化相机
camera = Camera()

# 玩家光源将在玩家初始化后添加
player_light_index = -1  # 初始化为-1，表示尚未创建

# 迷宫相关常量
MAZE_WIDTH = 75  # 迷宫宽度（格子数）
MAZE_HEIGHT = 75  # 迷宫高度（格子数）
WALL_COLOR = (20, 50, 50)  # 墙壁颜色
PATH_COLOR = (0, 0, 0)  # 通道颜色

# Colors
BLACK = (5, 3, 1)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 12, 128)  # 哥布林
BROWN = (165, 70, 42)   # 兽人
GRAY = (128, 128, 128)  # 骷髅
ORANGE = (255, 165, 21)  # 史莱姆
GOLD = (255, 215, 0)  # 免疫力颜色
PINK = (255, 2, 2)  # 回血包颜色
WALL_GRADIENT = [(0, 0, 150), (0, 0, 200)]  # 墙壁渐变色
PLAYER_GLOW = (255, 255, 100)  # 玩家光晕颜色
SHADOW_COLOR = (0, 0, 0, 100)  # 半透明阴影

# 视野限制相关常量
FOG_OF_WAR_ENABLED = True  # 是否启用战争迷雾效果
VISIBILITY_RADIUS = 300    # 玩家视野半径

# 在颜色常量下方添加武器相关常量
WEAPON_TYPES = {
    "Wooden Sword": {"attack": 8, "color": BROWN},
    "Iron Sword": {"attack": 15, "color": GRAY},
    "Steel Sword": {"attack": 25, "color": WHITE},
    "Magic Sword": {"attack": 35, "color": PURPLE},
    "Pistol": {"attack": 20, "color": (0, 0, 0)},  # 黑色
    "Rifle": {"attack": 30, "color": (255, 0, 0)},  # 红色
    "Shotgun": {"attack": 40, "color": (0, 255, 0)}  # 绿色
}

# Game settings
CELL_SIZE = 40
GAME_WIDTH = MAZE_WIDTH * CELL_SIZE
GAME_HEIGHT = MAZE_HEIGHT * CELL_SIZE

# 在全局变量区域添加这些量（根据用户记忆优化）
MAX_MONSTERS = 300 # 设置最大病毒数量（翻倍）
MIN_MONSTERS = 40   # 最小病毒数量（翻倍）
MONSTER_SPAWN_COOLDOWN = 180  # 刷新冷却时间（180帧，约3秒）
MAX_HEALTH_PACKS = 40   # 场上最大回血包数量
HEALTH_PACK_SPAWN_COOLDOWN = 100  # 回血包刷新冷却时间（?秒）
HEALTH_RESTORE_AMOUNT = 20  # 回血包恢复量

# 难度增长优化：从每1分调整为每100分
DIFFICULTY_SCORE_THRESHOLD = 1000  # 每1000分增加一次难度

# 在全局变量区域添加技能相关常量
SKILL_UPGRADE_COST = 500  # 技能升级所需免疫力

SKILLS = {
    "Area Attack": {
        "key": pygame.K_SPACE,
        "damage": 50,
        "range": 200,
        "cooldown": 600,  # 10秒 (600帧 ÷ 60帧/秒 = 10秒)
        "color": YELLOW,  # 直接使用已定义的颜色常量
        "description": "Damage nearby enemies",
        "level": 1  # 初始等级
    },
    "Heal": {
        "key": pygame.K_f,
        "heal": 50,
        "cooldown": 6,  # 0.1秒
        "color": GREEN,  # 直接使用已定义的颜色常量
        "description": "Restore HP",
        "level": 1  # 初始等级
    },
    "Flash": {
        "key": pygame.K_e,
        "distance": 200,
        "cooldown": 6,  # 0.1秒
        "color": BLUE,  # 直接使用已定义的颜色常量
        "description": "Quick teleport",
        "level": 1  # 初始等级
    },
    "Invincible": {
        "key": pygame.K_t,  # 改为T键，避免与新的R键技能冲突
        "duration": 180,
        "cooldown": 6,  # 0.1秒
        "color": GOLD,  # 直接使用已定义的颜色常量
        "description": "Temporary invincibility",
        "level": 1  # 初始等级
    },
    "Multi Shot": {
        "key": pygame.K_r,  # 新增R键多重射击技能
        "damage": 25,  # 每颗子弹的伤害
        "bullet_count": 50,  # 子弹数量
        "cooldown": 180,  # 3秒冷却时间
        "color": (212, 223, 7),  # 金色
        "description": "Multi-directional burst shot",
        "level": 1  # 初始等级
    }
}

# Boss病毒类型定义
BOSS_TYPES = [
    {
        "name": "超级流感",
        "hp": 300,
        "attack": 30,
        "defense": 15,
        "color": (180, 30, 30),  # 深红色
        "size_multiplier": 5,  # Boss体型翻倍
        "exp_multiplier": 10    # 免疫力奖励翻10倍
    },
    {
        "name": "病毒之王",
        "hp": 250,
        "attack": 35,
        "defense": 12,
        "color": (100, 20, 120),  # 紫黑色
        "size_multiplier": 1.8,
        "exp_multiplier": 2.5
    }
]

# 武器管理工具函数
def upgrade_weapon():
    """升级武器的统一函数"""
    global player_weapon, player_attack
    weapon_names = list(WEAPON_TYPES.keys())
    current_weapon_index = weapon_names.index(player_weapon.name)
    
    if current_weapon_index < len(weapon_names) - 1:
        new_weapon_name = weapon_names[current_weapon_index + 1]
        player_weapon = Weapon(
            new_weapon_name,
            WEAPON_TYPES[new_weapon_name]["attack"],
            WEAPON_TYPES[new_weapon_name]["color"]
        )
        player_attack = player_base_attack + player_weapon.attack_bonus
        return True
    return False

def downgrade_weapon():
    """降级武器的统一函数"""
    global player_weapon, player_attack
    weapon_names = list(WEAPON_TYPES.keys())
    current_weapon_index = weapon_names.index(player_weapon.name)
    
    if current_weapon_index > 0:
        new_weapon_name = weapon_names[current_weapon_index - 1]
        player_weapon = Weapon(
            new_weapon_name,
            WEAPON_TYPES[new_weapon_name]["attack"],
            WEAPON_TYPES[new_weapon_name]["color"]
        )
        player_attack = player_base_attack + player_weapon.attack_bonus
        return True
    return False

class Weapon:
    def __init__(self, name, attack_bonus, color):
        self.name = name
        self.attack_bonus = attack_bonus
        self.color = color
        self.size = CELL_SIZE - 15
    
    def draw(self, window, x, y, camera_x, camera_y):
        # 绘制剑的形状
        screen_x = x - camera_x
        screen_y = y - camera_y
        
        # 绘制剑的形状
        pygame.draw.rect(window, self.color,
                        (screen_x - self.size//4,
                         screen_y - self.size//8,
                         self.size//2,
                         self.size//4))
        
        # 剑身
        pygame.draw.rect(window, self.color,
                        (screen_x - self.size//2,
                         screen_y - self.size//8,
                         self.size,
                         self.size//8))

class Monster:
    def __init__(self, x, y, name, hp, attack, defense, color, size_multiplier=1, exp_multiplier=1):
        self.x = x
        self.y = y
        self.name = name
        self.hp = int(hp * 1.5)  # 增加50%的生命值
        self.max_hp = int(hp * 1.5)
        self.attack = int(attack * 1.3)  # 增加30%的攻击力
        self.defense = int(defense * 1.2)  # 增加20%的防御力
        self.is_alive = True
        self.size = int((CELL_SIZE - 10) * size_multiplier)  # Boss会更大
        self.color = color
        self.speed = 7 if size_multiplier == 1 else 4  # 提高移动速度
        self.move_cooldown = 0
        self.move_direction = random.choice([(1,0), (-1,0), (0,1), (0,-1)])
        self.exp_reward = int((hp // 3) * exp_multiplier)  # Boss给更多免疫力
        self.font = FONT_TINY
        self.is_boss = size_multiplier > 1  # 标记是否为Boss
        
        # 添加攻击相关属性
        self.attack_cooldown = 0  # 攻击冷却时间
        self.attack_range = CELL_SIZE * 1  # 攻击范围（1格距离，从2格减少到1格）
        self.attack_cooldown_max = 100  # 攻击冷却时间（1.6秒）
    
    def draw(self, window, camera_x, camera_y):
        if not self.is_alive:
            return

        # 优化的视野剖除检查
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        margin = self.size + 20  # 增加margin以容纳光晕
        if (screen_x < -margin or screen_x > WINDOW_WIDTH + margin or
            screen_y < -margin or screen_y > WINDOW_HEIGHT + margin):
            return

        # 预计算底光效果
        if not hasattr(self, '_glow_surface'):
            glow_size = int(self.size * 1.8)
            self._glow_surface = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
            # 根据病毒类型选择光晕颜色
            glow_colors = {
                "感冒病毒": (100, 255, 100),      # 绿色
                "流感病毒": (255, 180, 80),       # 橙色
                "蛀牙细菌": (220, 220, 200),      # 米白色
                "鼻涕虫菌": (180, 255, 120),      # 黄绿色
                "肚子疼菌": (180, 120, 80),       # 棕色
                "熬夜菌": (200, 170, 255),        # 淡紫色
                "咳嗽病毒": (150, 150, 180),      # 灰蓝色
                "懒惰菌": (200, 200, 200),        # 灰色
                "坏情绪菌": (150, 80, 200),       # 紫色
                "发烧病毒": (255, 120, 80),       # 红橙色
                "超级流感": (255, 80, 80),        # 红色
                "病毒之王": (180, 80, 200),       # 紫黑色
            }
            glow_color = glow_colors.get(self.name, (255, 255, 255))
            # 绘制多层渐变光晕
            center = glow_size // 2
            for i in range(glow_size // 2, 0, -3):
                alpha = int(80 * (i / (glow_size // 2)))
                pygame.draw.circle(self._glow_surface, (*glow_color, alpha), (center, center), i)

        # 绘制底光（在病毒下方）
        glow_size = int(self.size * 1.8)
        window.blit(self._glow_surface,
                   (screen_x - glow_size // 2, screen_y - glow_size // 2))

        # 优化：使用预计算的阴影表面
        if not hasattr(self, '_shadow_surface'):
            self._shadow_surface = pygame.Surface((self.size, self.size//2), pygame.SRCALPHA)
            pygame.draw.ellipse(self._shadow_surface, (0, 0, 0, 100),
                              (0, 0, self.size, self.size//2))

        # 绘制阴影
        window.blit(self._shadow_surface,
                   (screen_x - self.size//2, screen_y + self.size//4))

        # 预计算带发光边框的病毒表面
        if not hasattr(self, '_monster_surface'):
            # 尝试使用图片
            monster_img = MONSTER_IMAGES.get(self.name)
            if monster_img is not None:
                # 缩放图片
                scaled_img = pygame.transform.scale(monster_img, (self.size, self.size))
                # 创建带边框的表面（稍大一点以容纳边框）
                border_size = max(2, self.size // 15)
                surface_size = self.size + border_size * 2
                self._monster_surface = pygame.Surface((surface_size, surface_size), pygame.SRCALPHA)
                # 绘制发光边框（多层实现柔和效果）
                glow_colors = {
                    "感冒病毒": (100, 255, 100),
                    "流感病毒": (255, 180, 80),
                    "蛀牙细菌": (220, 220, 200),
                    "鼻涕虫菌": (180, 255, 120),
                    "肚子疼菌": (180, 120, 80),
                    "熬夜菌": (200, 170, 255),
                    "咳嗽病毒": (150, 150, 180),
                    "懒惰菌": (200, 200, 200),
                    "坏情绪菌": (150, 80, 200),
                    "发烧病毒": (255, 120, 80),
                    "超级流感": (255, 80, 80),
                    "病毒之王": (180, 80, 200),
                }
                border_color = glow_colors.get(self.name, (255, 255, 255))
                # 外层光晕
                for i in range(border_size, 0, -1):
                    alpha = int(150 * (i / border_size))
                    rect = (border_size - i, border_size - i,
                           self.size + i * 2, self.size + i * 2)
                    pygame.draw.rect(self._monster_surface, (*border_color, alpha), rect,
                                   border_radius=max(3, self.size // 8))
                # 绘制病毒图片
                self._monster_surface.blit(scaled_img, (border_size, border_size))
                self._border_offset = border_size
            else:
                # 回退到默认的圆形渲染
                self._monster_surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
                self._border_offset = 0

                # 创建渐变效果
                for i in range(self.size//2, 0, -2):
                    alpha = max(50, 255 - (self.size//2 - i) * 8)
                    color = [max(0, min(255, c)) for c in self.color]
                    pygame.draw.circle(self._monster_surface, (*color, alpha),
                                     (self.size//2, self.size//2), i)

                # 高光效果
                highlight_size = self.size//4
                highlight = pygame.Surface((highlight_size, highlight_size), pygame.SRCALPHA)
                pygame.draw.circle(highlight, (255, 255, 255, 150),
                                 (highlight_size//2, highlight_size//2), highlight_size//2)
                self._monster_surface.blit(highlight, (self.size//4, self.size//4))

        # 绘制病毒
        border_offset = getattr(self, '_border_offset', 0)
        window.blit(self._monster_surface,
                   (screen_x - self.size//2 - border_offset,
                    screen_y - self.size//2 - border_offset))

        # 优化的血条绘制
        self._draw_health_bar(window, screen_x, screen_y)
    
    def _draw_health_bar(self, window, screen_x, screen_y):
        """优化的血条绘制方法"""
        hp_bar_width = self.size
        hp_bar_height = 5
        hp_bar_x = screen_x - hp_bar_width//2
        hp_bar_y = screen_y - self.size//2 - 15
        
        # 血条边框（只在边框绘制）
        pygame.draw.rect(window, (40, 40, 40),
                       (hp_bar_x-1, hp_bar_y-1, hp_bar_width+2, hp_bar_height+2))
        
        # 血条背景
        pygame.draw.rect(window, (100, 45, 21),
                       (hp_bar_x, hp_bar_y, hp_bar_width, hp_bar_height))
        
        # 当前血量条（优化颜色计算）
        hp_percentage = self.hp / self.max_hp
        current_width = int(hp_bar_width * hp_percentage)
        if current_width > 0:
            # 使用简单的颜色插值
            green_component = int(255 * hp_percentage)
            red_component = int(255 * (1 - hp_percentage))
            hp_color = (red_component, green_component, 0)
            pygame.draw.rect(window, hp_color,
                           (hp_bar_x, hp_bar_y, current_width, hp_bar_height))
    
    def check_collision(self, player_x, player_y, player_size):
        if not self.is_alive:
            return False
        distance = ((player_x - self.x) ** 2 + (player_y - self.y) ** 2) ** 0.5
        return distance < (player_size + self.size) // 2
    
    def can_attack_player(self, player_x, player_y):
        """检查是否在攻击范围内且冷却时间结束"""
        if not self.is_alive or self.attack_cooldown > 0:
            return False
        distance = ((player_x - self.x) ** 2 + (player_y - self.y) ** 2) ** 0.5
        return distance <= self.attack_range
    
    def attack_player(self, player_x, player_y):
        """攻击玩家并设置冷却时间"""
        if self.can_attack_player(player_x, player_y):
            self.attack_cooldown = self.attack_cooldown_max
            return True
        return False
    
    def update_attack_cooldown(self):
        """更新攻击冷却时间"""
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
    
    def take_damage(self, damage):
        actual_damage = max(damage - self.defense, 0)
        self.hp = max(self.hp - actual_damage, 0)
        if self.hp <= 0:
            self.is_alive = False
            
    def attack_target(self, target):
        if self.is_alive:
            target.take_damage(self.attack)
    
    def heal(self, amount):
        if self.is_alive:
            self.hp = min(self.hp + amount, self.max_hp)
            
    def __str__(self):
        return f"{self.name} (HP: {self.hp}/{self.max_hp})"
    
    def check_valid_position(self, x, y, maze):
        size = self.size // 2
        corners = [
            (int((x - size) // CELL_SIZE), int((y - size) // CELL_SIZE)),
            (int((x + size) // CELL_SIZE), int((y - size) // CELL_SIZE)),
            (int((x - size) // CELL_SIZE), int((y + size) // CELL_SIZE)),
            (int((x + size) // CELL_SIZE), int((y + size) // CELL_SIZE))
        ]
        
        for cell_x, cell_y in corners:
            if (not (0 <= cell_x < MAZE_WIDTH and 0 <= cell_y < MAZE_HEIGHT) or
                maze[cell_y][cell_x] == 1):
                return False
        return True

    def move_towards_player(self, player_x, player_y, maze=None, always_move=True):
        """
        病毒移动逻辑
        always_move: 是否始终移动（即使不在玩家视野内也自由游荡）
        """
        if not self.is_alive:
            return

        # 优化：提前执行移动冷却检查
        if self.move_cooldown > 0:
            self.move_cooldown -= 1
            return

        # 计算到玩家的距离（使用整数运算优化）
        dx_raw = player_x - self.x
        dy_raw = player_y - self.y
        distance_squared = dx_raw * dx_raw + dy_raw * dy_raw
        tracking_range_squared = (CELL_SIZE * 8) * (CELL_SIZE * 8)  # 增加追踪范围到8格

        # 在追踪范围内才会自动靠近玩家
        if distance_squared < tracking_range_squared:
            # 使用快速距离近似避免开方运算
            distance = (distance_squared) ** 0.5 if distance_squared > 0 else 0

            if distance > 0:
                dx = (dx_raw / distance) * self.speed
                dy = (dy_raw / distance) * self.speed
            else:
                dx = dy = 0
        else:
            # 自由游荡模式：即使不在玩家附近也会移动
            # 增加方向改变频率，让病毒更活跃
            if random.random() < 0.05:  # 5%的概率改变方向
                self.move_direction = random.choice([(1,0), (-1,0), (0,1), (0,-1), (1,1), (-1,-1), (1,-1), (-1,1)])

            dx = self.move_direction[0] * self.speed * 0.6  # 游荡时速度稍慢
            dy = self.move_direction[1] * self.speed * 0.6
        
        # 边界检查优化，增加边界缓冲区
        buffer = self.size // 2 + 5  # 增加5像素缓冲区
        next_x = max(buffer, min(GAME_WIDTH - buffer, self.x + dx))
        next_y = max(buffer, min(GAME_HEIGHT - buffer, self.y + dy))
        
        # 迷宫碰撞检测优化 - 改进的防卡墙系统
        if maze is not None:
            if self.check_valid_position(next_x, next_y, maze):
                self.x = next_x
                self.y = next_y
            else:
                # 改进的避障逻辑 - 多方向尝试
                moved = False
                
                # 首先尝试分别在x和y方向移动
                if self.check_valid_position(next_x, self.y, maze):
                    self.x = next_x
                    moved = True
                elif self.check_valid_position(self.x, next_y, maze):
                    self.y = next_y
                    moved = True
                
                # 如果单方向移动也失败，使用智能寻路
                if not moved and distance_squared < tracking_range_squared:
                    self._smart_pathfinding(player_x, player_y, maze)
                    moved = True
                
                # 如果仍然无法移动，执行防卡墙逃脱机制
                if not moved:
                    self._escape_from_wall(maze)
        else:
            self.x = next_x
            self.y = next_y
            
        # 统一的冷却管理，防止卡墙
        self.move_cooldown = 2  # 减少冷却时间提高响应性
    
    def _smart_pathfinding(self, player_x, player_y, maze):
        """优化的智能寻路算法"""
        player_dx = player_x - self.x
        player_dy = player_y - self.y
        
        # 增加更多的寻路方向选择
        if abs(player_dx) > abs(player_dy):
            # 优先垂直绕行
            directions = [(0, -self.speed), (0, self.speed), (-self.speed//2, -self.speed//2), (self.speed//2, self.speed//2)]
        else:
            # 优先水平绕行
            directions = [(-self.speed, 0), (self.speed, 0), (-self.speed//2, -self.speed//2), (self.speed//2, self.speed//2)]
        
        # 添加斜向移动尝试
        diagonal_directions = [
            (-self.speed//2, -self.speed//2), (self.speed//2, -self.speed//2),
            (-self.speed//2, self.speed//2), (self.speed//2, self.speed//2)
        ]
        directions.extend(diagonal_directions)
        
        for dx, dy in directions:
            buffer = self.size // 2 + 5
            test_x = max(buffer, min(GAME_WIDTH - buffer, self.x + dx))
            test_y = max(buffer, min(GAME_HEIGHT - buffer, self.y + dy))
            
            if self.check_valid_position(test_x, test_y, maze):
                self.x = test_x
                self.y = test_y
                return
        
        # 如果所有方向都被阻挡，强制改变方向并减少移动步长
        self.move_direction = random.choice([(1,0), (-1,0), (0,1), (0,-1)])
        self._escape_from_wall(maze)
    
    def _escape_from_wall(self, maze):
        """防卡墙逃脱机制"""
        # 尝试8个方向的小步移动来逃脱卡墙
        escape_directions = [
            (1, 0), (-1, 0), (0, 1), (0, -1),
            (1, 1), (-1, -1), (1, -1), (-1, 1)
        ]
        
        escape_distance = self.speed // 3  # 使用较小的逃脱距离
        
        for dx, dy in escape_directions:
            escape_x = self.x + dx * escape_distance
            escape_y = self.y + dy * escape_distance
            
            # 确保不越界
            buffer = self.size // 2 + 10  # 增加更大的缓冲区
            escape_x = max(buffer, min(GAME_WIDTH - buffer, escape_x))
            escape_y = max(buffer, min(GAME_HEIGHT - buffer, escape_y))
            
            if self.check_valid_position(escape_x, escape_y, maze):
                self.x = escape_x
                self.y = escape_y
                # 重置移动方向
                self.move_direction = (dx, dy)
                return
        
        # 如果仍然无法逃脱，强制传送到最近的有效位置
        self._force_teleport_to_valid_position(maze)
    
    def _force_teleport_to_valid_position(self, maze):
        """强制传送到最近的有效位置（最后手段）"""
        # 在周围寻找最近的有效位置
        search_radius = CELL_SIZE
        max_radius = CELL_SIZE * 3
        
        while search_radius <= max_radius:
            for angle in range(0, 360, 45):  # 每45度检查一次
                radian = math.radians(angle)
                test_x = self.x + math.cos(radian) * search_radius
                test_y = self.y + math.sin(radian) * search_radius
                
                # 确保不越界
                buffer = self.size // 2 + 10
                test_x = max(buffer, min(GAME_WIDTH - buffer, test_x))
                test_y = max(buffer, min(GAME_HEIGHT - buffer, test_y))
                
                if self.check_valid_position(test_x, test_y, maze):
                    self.x = test_x
                    self.y = test_y
                    return
            
            search_radius += CELL_SIZE // 2

# 修改玩家移动检查函数
def check_player_collision_with_maze(x, y, maze):
    # 获取玩家四个角的格子坐标
    player_radius = player_size // 2
    corners = [
        (int((x - player_radius) // CELL_SIZE), int((y - player_radius) // CELL_SIZE)),
        (int((x + player_radius) // CELL_SIZE), int((y - player_radius) // CELL_SIZE)),
        (int((x - player_radius) // CELL_SIZE), int((y + player_radius) // CELL_SIZE)),
        (int((x + player_radius) // CELL_SIZE), int((y + player_radius) // CELL_SIZE))
    ]
    
    # 检查每个角是否与墙壁碰撞
    for cell_x, cell_y in corners:
        if (0 <= cell_x < MAZE_WIDTH and 0 <= cell_y < MAZE_HEIGHT and
            maze[cell_y][cell_x] == 1):
            return True  # 碰撞
    return False  # 无碰撞

# 检查与迷宫的碰撞
def check_collision_with_maze(x, y, size, maze):
    # 获取实体四个角的格子坐标
    radius = size // 2
    corners = [
        (int((x - radius) // CELL_SIZE), int((y - radius) // CELL_SIZE)),
        (int((x + radius) // CELL_SIZE), int((y - radius) // CELL_SIZE)),
        (int((x - radius) // CELL_SIZE), int((y + radius) // CELL_SIZE)),
        (int((x + radius) // CELL_SIZE), int((y + radius) // CELL_SIZE))
    ]
    
    # 检查每个角是否与墙壁碰撞
    for cell_x, cell_y in corners:
        if (0 <= cell_x < MAZE_WIDTH and 0 <= cell_y < MAZE_HEIGHT and
            maze[cell_y][cell_x] == 1):
            return True  # 碰撞
    return False  # 无碰撞

class HealthPack:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = CELL_SIZE - 15
        self.active = True
    
    def draw(self, window, camera_x, camera_y):
        if self.active:
            # 绘制十字形状的回血包
            center_x = self.x - camera_x
            center_y = self.y - camera_y
            rect_width = self.size // 3
            rect_height = self.size
            
            # 绘制垂直部分
            pygame.draw.rect(window, PINK,
                           (center_x - rect_width//2,
                            center_y - rect_height//2,
                            rect_width, rect_height))
            
            # 绘制水平部分
            pygame.draw.rect(window, PINK,
                           (center_x - rect_height//2,
                            center_y - rect_width//2,
                            rect_height, rect_width))
    
    def check_collision(self, player_x, player_y, player_size):
        if not self.active:
            return False
        distance = ((player_x - self.x) ** 2 + (player_y - self.y) ** 2) ** 0.5
        return distance < (player_size + self.size) // 2

def generate_monsters(num_monsters):
    monsters = []
    # 病毒类型定义
    monster_types = [
        {"name": "感冒病毒", "hp": 40, "attack": 12, "defense": 2, "color": (100, 200, 100)},
        {"name": "流感病毒", "hp": 55, "attack": 15, "defense": 4, "color": (255, 150, 50)},
        {"name": "蛀牙细菌", "hp": 35, "attack": 14, "defense": 1, "color": (200, 200, 180)},
        {"name": "鼻涕虫菌", "hp": 30, "attack": 10, "defense": 1, "color": (180, 220, 100)},
        {"name": "肚子疼菌", "hp": 85, "attack": 18, "defense": 6, "color": (139, 90, 43)},
        {"name": "熬夜菌", "hp": 45, "attack": 16, "defense": 0, "color": (180, 150, 220)},
        {"name": "咳嗽病毒", "hp": 25, "attack": 8, "defense": 0, "color": (100, 100, 120)},
        {"name": "懒惰菌", "hp": 99, "attack": 14, "defense": 15, "color": (169, 169, 169)},
        {"name": "坏情绪菌", "hp": 50, "attack": 22, "defense": 3, "color": (100, 50, 150)},
        {"name": "发烧病毒", "hp": 60, "attack": 20, "defense": 4, "color": (255, 80, 50)}
    ]

    def check_monster_collision(x, y, size, existing_monsters):
        for monster in existing_monsters:
            distance = ((x - monster.x) ** 2 + (y - monster.y) ** 2) ** 0.5
            if distance < (size + monster.size) // 2:
                return True
        return False

    # 有10%的概率生成Boss
    if random.random() < 0.1:
        boss_type = random.choice(BOSS_TYPES)
        if _spawn_monster_safely(monsters, boss_type, is_boss=True):
            pass  # Boss生成成功

    # 生成普通怪物
    for _ in range(num_monsters):
        monster_type = random.choice(monster_types)
        _spawn_monster_safely(monsters, monster_type, is_boss=False)
    
    # 确保生成的怪物数量不超过最大数量
    return monsters[:MAX_MONSTERS]

def _spawn_monster_safely(monsters, monster_type, is_boss=False):
    """安全生成怪物的助手函数"""
    attempts = 0
    max_attempts = 100  # 增加尝试次数
    
    while attempts < max_attempts:
        x = random.randint(CELL_SIZE * 2, GAME_WIDTH - CELL_SIZE * 2)  # 给边界留更多空间
        y = random.randint(CELL_SIZE * 2, GAME_HEIGHT - CELL_SIZE * 2)
        
        if is_boss:
            size_multiplier = monster_type["size_multiplier"]
            exp_multiplier = monster_type["exp_multiplier"]
            monster_size = int((CELL_SIZE - 10) * size_multiplier)
        else:
            size_multiplier = 1
            exp_multiplier = 1
            monster_size = CELL_SIZE - 10
        
        # 检查是否与现有怪物冲突
        collision_found = False
        for monster in monsters:
            distance = ((x - monster.x) ** 2 + (y - monster.y) ** 2) ** 0.5
            if distance < (monster_size + monster.size) // 2 + 20:  # 增加安全距离
                collision_found = True
                break
        
        # 检查是否在墙里（需要在迷宫初始化后才能检查）
        wall_collision = False
        try:
            wall_collision = check_collision_with_maze(x, y, monster_size, maze)
        except NameError:
            # 如果迷宫还没有初始化，跳过墙壁检测
            wall_collision = False
        
        if not collision_found and not wall_collision:
            monster = Monster(
                x, y,
                monster_type["name"],
                monster_type["hp"],
                monster_type["attack"],
                monster_type["defense"],
                monster_type["color"],
                size_multiplier=size_multiplier,
                exp_multiplier=exp_multiplier
            )
            monsters.append(monster)
            return True
        
        attempts += 1
    
    return False  # 生成失败

def generate_health_packs(num_packs):
    health_packs = []
    for _ in range(num_packs):
        # 在游戏区域内随机生成回血包
        pack_x = random.randint(CELL_SIZE, GAME_WIDTH - CELL_SIZE)
        pack_y = random.randint(CELL_SIZE, GAME_HEIGHT - CELL_SIZE)
        health_packs.append(HealthPack(pack_x, pack_y))
    return health_packs

# Set game center
center_x = GAME_WIDTH // 2
center_y = GAME_HEIGHT // 2

# Player properties
player_size = CELL_SIZE - 10
# 将玩家放在迷宫入口附近
player_x = CELL_SIZE * 1.5
player_y = CELL_SIZE * 1.5
player_speed = 30  # 增加基础速度
camera_x = 0
camera_y = 0

# 加载玩家图片
try:
    player_image = pygame.image.load(resource_path("中国球.png")).convert_alpha()
    # 缩放图片到适合的大小
    player_image = pygame.transform.scale(player_image, (player_size, player_size))
except (pygame.error, FileNotFoundError):
    print("警告：无法加载 中国球.png，将使用默认的圆形")
    player_image = None

# 加载武器图片
try:
    weapon_image_original = pygame.image.load(resource_path("铁剑.png")).convert_alpha()
    # 缩放武器图片
    weapon_image_original = pygame.transform.scale(weapon_image_original, (32, 32))
except (pygame.error, FileNotFoundError):
    print("警告：无法加载 铁剑.png，将使用默认的武器形状")
    weapon_image_original = None

# 加载病毒图片
MONSTER_IMAGES = {}
MONSTER_IMAGE_NAMES = [
    "感冒病毒", "流感病毒", "蛀牙细菌", "鼻涕虫菌", "肚子疼菌",
    "熬夜菌", "咳嗽病毒", "懒惰菌", "坏情绪菌", "发烧病毒",
    "超级流感", "病毒之王"
]
for monster_name in MONSTER_IMAGE_NAMES:
    try:
        img_path = resource_path(f"images/{monster_name}.png")
        img = pygame.image.load(img_path).convert_alpha()
        MONSTER_IMAGES[monster_name] = img
        print(f"已加载病毒图片: {monster_name}")
    except (pygame.error, FileNotFoundError):
        print(f"警告：无法加载 images/{monster_name}.png，将使用默认图形")
        MONSTER_IMAGES[monster_name] = None

# 玩家朝向和武器攻击相关变量
player_facing_angle = 0  # 玩家朝向角度（弧度）
player_facing_direction = "right"  # 玩家朝向方向
weapon_swing_angle = 0  # 武器挥动角度
weapon_is_swinging = False  # 是否正在挥动武器
weapon_swing_timer = 0  # 挥动计时器
WEAPON_SWING_DURATION = 15  # 挥动持续帧数

# 鼠标拖拽视角相关变量
mouse_dragging = False
last_mouse_x = 0
last_mouse_y = 0
camera_drag_speed = 1.0  # 拖拽灵敏度
camera_follow_player = True  # 默认跟随玩家，可以通过拖拽临时取消

player_hp = 100
player_max_hp = 100
player_base_attack = 20
player_weapon = Weapon("Wooden Sword", WEAPON_TYPES["Wooden Sword"]["attack"], WEAPON_TYPES["Wooden Sword"]["color"])
player_attack = player_base_attack + player_weapon.attack_bonus
player_defense = 5
player_exp = 0
player_level = 1
player_exp_to_next_level = 100
player_is_hit = False
player_hit_timer = 0

# 玩家光源已禁用（去掉黄色光圈）
player_light_index = -1

# 在Player properties部分修改技能相关属性
player_skills_cooldown = {name: 0 for name in SKILLS}
player_invincible = False
player_invincible_timer = 0
skill_effects = []  # 存储所有技能特效

# 在Player properties部分添加加速度相关属性
player_velocity_x = 0
player_velocity_y = 0
player_acceleration = 12.0  # 增加加速度
player_max_speed = 5  # 增加最大速度
player_friction = 0.9  # 保持摩擦力
player_dash_speed = 120  # 保持冲刺速度
player_dash_cooldown = 10
DASH_COOLDOWN_MAX = 20  # 保持冲刺冷却时间
is_dashing = False  # 初始化冲刺状态

# Game state
game_won = False
game_over = False
monsters = generate_monsters(60)  # 调整初始病毒数量为60个（翻倍）
combat_cooldown = 0
COMBAT_COOLDOWN_MAX = 30  # 战斗冷却时间（帧数）
monster_spawn_timer = 0
health_packs = generate_health_packs(1)  # 初始生成1个回血包
health_pack_spawn_timer = 0


# 迷宫生成函数
def generate_maze(width, height):
    # 初始化迷宫，1表示墙，0表示通道
    maze = [[1 for _ in range(width)] for _ in range(height)]
    
    # 使用深度优先搜索算法生成迷宫（改用栈避免递归深度问题）
    def carve_passages(x, y):
        # 使用栈代替递归
        stack = [(x, y)]
        maze[y][x] = 0  # 标记起点为通道
        
        while stack:
            cx, cy = stack[-1]  # 获取当前单元格
            
            # 随机选择方向：上、右、下、左
            directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
            random.shuffle(directions)
            
            moved = False
            for dx, dy in directions:
                nx, ny = cx + dx*2, cy + dy*2
                if 0 <= nx < width and 0 <= ny < height and maze[ny][nx] == 1:
                    # 在两个单元格之间挖通道
                    maze[cy + dy][cx + dx] = 0
                    maze[ny][nx] = 0
                    stack.append((nx, ny))
                    moved = True
                    break
            
            # 如果没有可移动的方向，回溯
            if not moved:
                stack.pop()
    
    # 从随机点开始生成
    start_x = random.randrange(1, width, 2)
    start_y = random.randrange(1, height, 2)
    
    # 确保起点是奇数坐标
    if start_x % 2 == 0:
        start_x -= 1
    if start_y % 2 == 0:
        start_y -= 1
    
    carve_passages(start_x, start_y)
    
    # 确保入口和出口
    maze[1][1] = 0  # 入口附近
    maze[height-2][width-2] = 0  # 出口附近
    
    # 添加一些额外的通道，使迷宫不那么复杂
    for _ in range(width * height // 20):  # 添加约5%的额外通道
        x = random.randrange(1, width-1)
        y = random.randrange(1, height-1)
        maze[y][x] = 0
    
    return maze

# 迷宫绘制函数（优化版）
def draw_maze(window, maze, camera_x, camera_y):
    # 优化：使用更精确的可见区域计算
    start_x = max(0, int(camera_x // CELL_SIZE) - 1)  # 加上边界缓冲
    end_x = min(MAZE_WIDTH, int((camera_x + WINDOW_WIDTH) // CELL_SIZE + 2))
    start_y = max(0, int(camera_y // CELL_SIZE) - 1)
    end_y = min(MAZE_HEIGHT, int((camera_y + WINDOW_HEIGHT) // CELL_SIZE + 2))
    
    # 使用预渲染的墙壁纹理
    global wall_texture_cache
    if 'wall_texture_cache' not in globals():
        wall_texture_cache = create_wall_texture()
    
    # 只绘制可见区域的单元格
    for y in range(start_y, end_y):
        for x in range(start_x, end_x):
            if y < len(maze) and x < len(maze[0]) and maze[y][x] == 1:  # 墙
                screen_x = x * CELL_SIZE - camera_x
                screen_y = y * CELL_SIZE - camera_y
                window.blit(wall_texture_cache, (screen_x, screen_y))

def create_wall_texture():
    """创建一次性预渲染的墙壁纹理"""
    wall_surface = pygame.Surface((CELL_SIZE, CELL_SIZE))
    
    # 绘制基础墙壁
    wall_surface.fill(WALL_COLOR)
    
    # 添加简化的纹理效果（减少随机元素）
    texture_color = (30, 30, 120)
    for i in range(0, CELL_SIZE, 8):  # 用固定模式替代随机
        pygame.draw.line(wall_surface, texture_color, (i, 0), (i, CELL_SIZE), 1)
        pygame.draw.line(wall_surface, texture_color, (0, i), (CELL_SIZE, i), 1)
    
    # 添加边缘高光
    pygame.draw.line(wall_surface, (70, 70, 170), (0, 0), (CELL_SIZE, 0), 2)
    pygame.draw.line(wall_surface, (70, 70, 170), (0, 0), (0, CELL_SIZE), 2)
    
    return wall_surface

# 生成迷宫
maze = generate_maze(MAZE_WIDTH, MAZE_HEIGHT)

# Game loop
running = True
clock = pygame.time.Clock()

# 计算初始速度（解决speed未定义问题）
speed = 0

# 初始化墙壁纹理缓存
wall_texture_cache = create_wall_texture()

# 2. 游戏平衡性优化
DIFFICULTY_SCALING = {
    'monster_hp_multiplier': 1.1,  # 每次生成怪物时HP增加10%
    'monster_damage_multiplier': 1.05,  # 每次生成怪物时伤害增加5%
    'exp_multiplier': 1.2  # 每次生成怪物时经验值增加20%
}

# 3. 添加游戏进保存功能
def save_game():
    game_state = {
        'player_level': player_level,
        'player_exp': player_exp,
        'player_hp': player_hp,
        'player_weapon': player_weapon.name,
        'monsters_killed': len([m for m in monsters if not m.is_alive])
    }
    with open('game_save.txt', 'w') as f:
        json.dump(game_state, f)

def load_game():
    try:
        with open('game_save.txt', 'r') as f:
            return json.load(f)
    except:
        return None

# 4. 添加游戏暂停功能
game_paused = False

# 把这个函数定义移到其他函数（如generate_monsters）之前
def is_in_view(x, y, camera_x, camera_y):
    screen_x = x - camera_x
    screen_y = y - camera_y
    margin = CELL_SIZE * 2
    return (-margin <= screen_x <= WINDOW_WIDTH + margin and 
            -margin <= screen_y <= WINDOW_HEIGHT + margin)

# 在文件顶部添加子弹类
class Bullet:
    def __init__(self, x, y, direction, speed, color):
        self.x = x
        self.y = y
        self.direction = direction  # 方向是一个元组 (dx, dy)
        self.speed = speed
        self.color = color
        self.size = 5  # 子弹大小

    def update(self):
        self.x += self.direction[0] * self.speed
        self.y += self.direction[1] * self.speed

    def draw(self, window, camera_x, camera_y):
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        pygame.draw.circle(window, self.color, (int(screen_x), int(screen_y)), self.size)

# 在Player properties部分添加子弹列表
player_bullets = []

# 在文件顶部定义关卡数据
LEVELS = {
    1: {"monster_count": 160, "boss": False},   # 翻倍
    2: {"monster_count": 200, "boss": False},   # 翻倍
    3: {"monster_count": 240, "boss": True},    # 翻倍
    4: {"monster_count": 300, "boss": False},   # 翻倍
    5: {"monster_count": 360, "boss": True},    # 翻倍
    6: {"monster_count": 400, "boss": False},   # 翻倍
    7: {"monster_count": 500, "boss": True},    # 翻倍
    8: {"monster_count": 600, "boss": False},   # 翻倍
    9: {"monster_count": 700, "boss": True},    # 翻倍
    10: {"monster_count": 800, "boss": True}    # 翻倍
}

current_level_index = 1  # 当前关卡索引，从1开始
current_level = LEVELS[current_level_index]  # 当前关卡

def load_level(level_index):
    global current_level
    current_level = LEVELS[level_index]
    # 生成怪物
    monsters = generate_monsters(current_level["monster_count"])
    return monsters

# 在Player properties部分添加player_angle
player_angle = 0  # 初始化玩家角度

# 在Player properties部分添加穿墙状态
no_clip_mode = False  # 穿墙模式状态

# 在文件顶部添加对话类
class Dialogue:
    def __init__(self):
        self.messages = []
        self.current_message_index = 0
        self.is_active = False

    def add_message(self, message):
        self.messages.append(message)

    def start(self):
        if self.messages:
            self.is_active = True
            self.current_message_index = 0

    def next_message(self):
        if self.is_active:
            self.current_message_index += 1
            if self.current_message_index >= len(self.messages):
                self.is_active = False

    def draw(self, window):
        if self.is_active:
            text = FONT_SMALL.render(self.messages[self.current_message_index], True, YELLOW)
            text_rect = text.get_rect()
            # 显示在屏幕顶部中央，带背景框
            x = (WINDOW_WIDTH - text_rect.width) // 2
            y = 5
            # 绘制半透明背景
            bg_rect = pygame.Rect(x - 10, y - 3, text_rect.width + 20, text_rect.height + 6)
            bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
            bg_surface.fill((0, 0, 0, 180))
            window.blit(bg_surface, (bg_rect.x, bg_rect.y))
            pygame.draw.rect(window, YELLOW, bg_rect, 1)
            window.blit(text, (x, y))

# 商店类
class Shop:
    def __init__(self):
        self.items = {
            "Health Pack": {"cost": 50, "description": "Restores 50 HP"},
            "Iron Sword": {"cost": 100, "description": "Increases attack by 15"},
            "Steel Sword": {"cost": 200, "description": "Increases attack by 25"},
        }
        self.is_open = False

    def toggle_shop(self):
        """切换商店开关"""
        self.is_open = not self.is_open

    def display_items(self, window):
        """显示商店物品"""
        if not self.is_open:
            return
            
        # 绘制商店背景
        shop_width = 400
        shop_height = 300
        shop_x = (WINDOW_WIDTH - shop_width) // 2
        shop_y = (WINDOW_HEIGHT - shop_height) // 2

        pygame.draw.rect(window, (50, 50, 50), (shop_x, shop_y, shop_width, shop_height))
        pygame.draw.rect(window, WHITE, (shop_x, shop_y, shop_width, shop_height), 3)

        title_text = FONT_LARGE.render("商店 (按S关闭)", True, WHITE)
        window.blit(title_text, (shop_x + 10, shop_y + 10))

        y_offset = shop_y + 50
        item_index = 1
        for item_name, item_info in self.items.items():
            item_text = f"[{item_index}] {item_name}: {item_info['cost']} 免疫力"
            desc_text = f"    {item_info['description']}"

            color = GREEN if player_exp >= item_info['cost'] else RED
            item_surface = FONT_LARGE.render(item_text, True, color)
            desc_surface = FONT_SMALL.render(desc_text, True, WHITE)

            window.blit(item_surface, (shop_x + 10, y_offset))
            window.blit(desc_surface, (shop_x + 10, y_offset + 30))
            y_offset += 60
            item_index += 1

    def buy_item(self, item_name):
        """从商店购买物品"""
        global player_exp, player_hp, player_max_hp, player_weapon, player_attack, health_packs
        
        if item_name in self.items:
            item_cost = self.items[item_name]["cost"]
            if player_exp >= item_cost:
                player_exp -= item_cost
                
                if item_name == "Health Pack":
                    # 直接恢复生命值
                    player_hp = min(player_hp + 50, player_max_hp)
                    return True
                elif item_name == "Iron Sword":
                    if player_weapon.name == "Wooden Sword":
                        player_weapon = Weapon("Iron Sword", WEAPON_TYPES["Iron Sword"]["attack"], WEAPON_TYPES["Iron Sword"]["color"])
                        player_attack = player_base_attack + player_weapon.attack_bonus
                        return True
                elif item_name == "Steel Sword":
                    if player_weapon.name in ["Wooden Sword", "Iron Sword"]:
                        player_weapon = Weapon("Steel Sword", WEAPON_TYPES["Steel Sword"]["attack"], WEAPON_TYPES["Steel Sword"]["color"])
                        player_attack = player_base_attack + player_weapon.attack_bonus
                        return True
                        
        return False

# 在游戏主循环中添加对话逻辑
player_monster_dialogue = Dialogue()

# 示例对话内容
player_monster_dialogue.add_message("发现病毒入侵！")
player_monster_dialogue.add_message("准备消灭它们！")

# 在适当的地方启动对话，例如在玩家接近病毒时
for monster in monsters:
    if monster.check_collision(player_x, player_y, player_size):
        player_monster_dialogue.start()

def find_safe_spawn_position(start_x, start_y, maze):
    """寻找一个不在墙内的安全重生位置"""
    # 首先检查起始位置是否安全
    if not check_collision_with_maze(start_x, start_y, player_size, maze):
        return start_x, start_y

    # 螺旋搜索安全位置
    search_radius = CELL_SIZE
    max_radius = CELL_SIZE * 20  # 最大搜索半径

    while search_radius <= max_radius:
        # 在当前半径上搜索8个方向
        for angle in range(0, 360, 45):
            radian = math.radians(angle)
            test_x = start_x + math.cos(radian) * search_radius
            test_y = start_y + math.sin(radian) * search_radius

            # 确保在游戏边界内
            test_x = max(CELL_SIZE * 2, min(GAME_WIDTH - CELL_SIZE * 2, test_x))
            test_y = max(CELL_SIZE * 2, min(GAME_HEIGHT - CELL_SIZE * 2, test_y))

            # 检查是否安全
            if not check_collision_with_maze(test_x, test_y, player_size, maze):
                return test_x, test_y

        search_radius += CELL_SIZE // 2

    # 如果找不到安全位置，返回迷宫入口附近
    return CELL_SIZE * 1.5, CELL_SIZE * 1.5

def respawn_player():
    global player_x, player_y, player_hp, player_is_hit, player_hit_timer

    # 尝试在游戏中心重生，如果卡墙则寻找安全位置
    target_x = GAME_WIDTH // 2
    target_y = GAME_HEIGHT // 2

    # 寻找安全的重生位置
    safe_x, safe_y = find_safe_spawn_position(target_x, target_y, maze)
    player_x = safe_x
    player_y = safe_y

    # Reset player health
    player_hp = player_max_hp
    # Reset hit status
    player_is_hit = False
    player_hit_timer = 0

# 初始化商店
shop = Shop()

# 在游戏主循环中处理对话和战斗逻辑
while running:
    # 事件处理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            # 优先处理复活按键（游戏结束时）
            if event.key == pygame.K_r and game_over:
                game_over = False
                respawn_player()
                continue
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_l:  # 按L键切换穿墙模式
                no_clip_mode = not no_clip_mode  # 切换穿墙状态
                
                # 添加穿墙特效
                effect_color = (0, 255, 255) if no_clip_mode else (255, 255, 255)  # 青色或白色
                for _ in range(20):
                    angle = random.uniform(0, math.pi * 2)
                    distance = random.uniform(15, 40)
                    particle_system.add_particle(
                        player_x + math.cos(angle) * distance,
                        player_y + math.sin(angle) * distance,
                        (*effect_color, 200),  # 特效颜色
                        math.cos(angle) * 2,
                        math.sin(angle) * 2,
                        30, 3, 0.9, 0
                    )
                
                # 添加状态视觉指示
                skill_effects.append({
                    "x": player_x,
                    "y": player_y,
                    "range": 60,
                    "color": effect_color,
                    "timer": 120  # 持续2秒
                })
                
                status_text = "穿墙模式开启" if no_clip_mode else "穿墙模式关闭"
                print(status_text)
            elif event.key == pygame.K_m:  # 按M键加强功能
                # 临时加强玩家能力
                player_base_attack += 10  # 增加10点攻击力
                player_max_speed += 2     # 增加移动速度
                player_defense += 5       # 增加5点防御力
                player_attack = player_base_attack + player_weapon.attack_bonus  # 更新总攻击力
                
                # 添加加强特效
                for _ in range(30):
                    angle = random.uniform(0, math.pi * 2)
                    distance = random.uniform(20, 60)
                    particle_system.add_particle(
                        player_x + math.cos(angle) * distance,
                        player_y + math.sin(angle) * distance,
                        (255, 215, 0, 200),  # 金色粒子
                        math.cos(angle) * 3,
                        math.sin(angle) * 3,
                        40, 4, 0.95, 0
                    )
                
                # 添加加强状态视觉效果
                skill_effects.append({
                    "x": player_x,
                    "y": player_y,
                    "range": 80,
                    "color": (255, 215, 0),  # 金色光环
                    "timer": 180  # 持续3秒
                })
                
                print("玩家加强！攻击力+10，速度+2，防御力+5")
            elif event.key == pygame.K_h:  # 按h键开启开挂
                player_hp = player_max_hp  # 血量恢复到最大
                player_exp += 1000  # 增加经验值
                # 检查是否可以升级
                while player_exp >= player_exp_to_next_level:
                    player_level += 1
                    player_exp -= player_exp_to_next_level
                    player_exp_to_next_level = int(player_exp_to_next_level * 1.2)  # 每级所需经验值增加20%
                    player_max_hp += 20  # 每级增加最大生命值
                    player_hp = player_max_hp  # 升级时回满血
                    player_base_attack += 5  # 每级增加基础攻击力
                    player_defense += 2  # 每级增加防御力
                    player_attack = player_base_attack + player_weapon.attack_bonus  # 更新攻击力
            elif event.key == pygame.K_o:  # 按O键升级武器
                upgrade_weapon()
            elif event.key == pygame.K_LSHIFT:  # 按住Shift键开始冲刺
                is_dashing = True  # 设置冲刺状态为True
            elif event.key == pygame.K_k:  # 按K键降级武器
                downgrade_weapon()
            elif event.key == pygame.K_q:  # 按Q键触发滑动攻击
                # 获取鼠标位置作为滑动方向
                mouse_x, mouse_y = pygame.mouse.get_pos()
                world_mouse_x = mouse_x + camera_x
                world_mouse_y = mouse_y + camera_y
                
                # 计算滑动角度
                dx = world_mouse_x - player_x
                dy = world_mouse_y - player_y
                distance = max(1, (dx**2 + dy**2)**0.5)  # 避免除零
                dx /= distance
                dy /= distance
                
                # 滑动参数
                slide_distance = 100  # 滑动距离
                slide_speed = 8       # 滑动速度（较慢）
                slide_step = 4        # 每帧移动距离
                
                # 计算滑动步数
                steps = int(slide_distance / slide_step)
                
                # 保存原始位置用于碰撞检测
                original_x, original_y = player_x, player_y
                
                # 逐帧滑动并检测碰撞
                for step in range(steps):
                    # 计算下一个位置
                    next_x = player_x + dx * slide_step
                    next_y = player_y + dy * slide_step
                    
                    # 限制在游戏边界内
                    next_x = max(player_size, min(GAME_WIDTH - player_size, next_x))
                    next_y = max(player_size, min(GAME_HEIGHT - player_size, next_y))
                    
                    # 检查是否与迷宫墙壁碰撞
                    if not no_clip_mode and check_collision_with_maze(next_x, next_y, player_size, maze):
                        # 如果碰撞墙壁，停止滑动
                        break
                    
                    # 更新玩家位置
                    player_x, player_y = next_x, next_y
                    
                    # 检测路径上的敌人
                    dash_range = 60  # 滑动范围（比冲撞范围小）
                    for monster in monsters[:]:
                        if monster.is_alive:
                            # 计算怪物到玩家当前位置的距离
                            monster_distance = ((monster.x - player_x) ** 2 + (monster.y - player_y) ** 2) ** 0.5
                            
                            # 如果怪物在滑动范围内
                            if monster_distance <= dash_range:
                                # 对怪物造成伤害
                                total_attack = int((player_base_attack + player_weapon.attack_bonus) * 1.2)  # 滑动伤害为普通攻击的1.2倍
                                monster.take_damage(total_attack)
                                
                                # 添加击退效果（比冲撞小）
                                knockback_distance = 15
                                monster.x += dx * knockback_distance
                                monster.y += dy * knockback_distance
                                
                                # 添加滑动击中特效
                                for _ in range(8):
                                    angle = random.uniform(0, math.pi * 2)
                                    particle_system.add_particle(
                                        monster.x + random.uniform(-8, 8),
                                        monster.y + random.uniform(-8, 8),
                                        (255, 255, 100, 200),  # 淡黄色滑动粒子
                                        math.cos(angle) * 2,
                                        math.sin(angle) * 2,
                                        20, 3, 0.9, 0
                                    )
                                
                                # 如果怪物死亡，获得经验值
                                if not monster.is_alive:
                                    player_exp += monster.exp_reward
                                    
                                    # 添加死亡特效
                                    for _ in range(15):
                                        angle = random.uniform(0, math.pi * 2)
                                        particle_system.add_particle(
                                            monster.x,
                                            monster.y,
                                            (255, 255, 100, 200),  # 淡黄色粒子
                                            math.cos(angle) * 4,
                                            math.sin(angle) * 4,
                                            25, 4, 0.95, 0
                                        )
                    
                    # 添加滑动轨迹特效
                    if step % 2 == 0:  # 每隔一帧添加特效以减少性能消耗
                        particle_system.add_particle(
                            player_x + random.uniform(-8, 8),
                            player_y + random.uniform(-8, 8),
                            (255, 255, 150, 150),  # 淡黄色轨迹粒子
                            random.uniform(-0.5, 0.5),
                            random.uniform(-0.5, 0.5),
                            15, 2, 0.9, 0
                        )
                
                # 添加滑动范围视觉效果
                skill_effects.append({
                    "x": player_x,
                    "y": player_y,
                    "range": 60,  # 滑动范围
                    "color": (255, 255, 100),  # 淡黄色滑动范围
                    "timer": 10
                })
            elif event.key == pygame.K_f:  # 按F键触发治疗技能
                # 治疗效果
                player_hp = min(player_hp + 50, player_max_hp)
                # 添加治疗粒子效果
                for _ in range(20):
                    angle = random.uniform(0, math.pi * 2)
                    distance = random.uniform(10, 40)
                    particle_system.add_particle(
                        player_x + math.cos(angle) * distance,
                        player_y + math.sin(angle) * distance,
                        (0, 255, 0, 200),  # 绿色粒子
                        math.cos(angle) * 1.5,
                        math.sin(angle) * 1.5,
                        30, 3, 0.95, 0
                    )
                skill_effects.append({
                    "x": player_x,
                    "y": player_y,
                    "range": 50,
                    "color": GREEN,
                    "timer": 30
                })
            elif event.key == pygame.K_SPACE:  # 按空格键继续对话
                player_monster_dialogue.next_message()
                # 移除有问题的对话结束逻辑
            elif event.key == pygame.K_u:  # 按U键升级技能
                for skill_name, skill in SKILLS.items():
                    if player_exp >= SKILL_UPGRADE_COST and skill["level"] < 3:  # 假设技能最多升级到3级
                        player_exp -= SKILL_UPGRADE_COST  # 扣除免疫力
                        skill["level"] += 1  # 提升技能等级
                        # 根据技能类型调整效果
                        if skill_name == "Area Attack":
                            skill["damage"] += 40  # 每级增加40点伤害
                        elif skill_name == "Heal":
                            skill["heal"] += 0  # 每级增加0点治疗量
                        elif skill_name == "Flash":
                            skill["distance"] += 100  # 每级增加50的闪现距离
                        elif skill_name == "Invincible":
                            skill["duration"] += 180  # 每级增加30帧的无敌时间
                        elif skill_name == "Multi Shot":
                            skill["bullet_count"] += 10  # 每级增加10颗子弹
                            skill["damage"] += 5  # 每级增加5点伤害
            elif event.key == pygame.K_i:  # 按I键自杀
                player_hp = 0
                game_over = True
            elif event.key == pygame.K_s:  # 按S键打开/关闭商店
                shop.toggle_shop()
            elif event.key == pygame.K_1 and shop.is_open:  # 在商店中按1键购买健康包
                if shop.buy_item("Health Pack"):
                    print("购买成功：健康包")
                else:
                    print("购买失败：免疫力不足")
            elif event.key == pygame.K_2 and shop.is_open:  # 在商店中按键购买铁剑
                if shop.buy_item("Iron Sword"):
                    print("购买成功：铁剑")
                else:
                    print("购买失败：免疫力不足或已拥有更高级武器")
            elif event.key == pygame.K_3 and shop.is_open:  # 在商店中按键购买钢剑
                if shop.buy_item("Steel Sword"):
                    print("购买成功：钢剑")
                else:
                    print("购买失败：免疫力不足或已拥有更高级武器")
        
        # 鼠标事件处理
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左键：近战攻击（根据用户记忆优化）
                # 触发武器挥动
                weapon_is_swinging = True
                weapon_swing_timer = WEAPON_SWING_DURATION

                # 计算攻击范围内的敌人
                attack_range = 60  # 攻击范围（根据用户记忆设为60像素）
                for monster in monsters:
                    if monster.is_alive:
                        distance = ((player_x - monster.x) ** 2 + (player_y - monster.y) ** 2) ** 0.5
                        if distance <= attack_range:
                            # 对怪物造成伤害
                            total_attack = player_base_attack + player_weapon.attack_bonus
                            monster.take_damage(total_attack)
                            
                            # 添加攻击特效
                            for _ in range(10):
                                angle = random.uniform(0, math.pi * 2)
                                particle_system.add_particle(
                                    monster.x + random.uniform(-10, 10),
                                    monster.y + random.uniform(-10, 10),
                                    (255, 100, 100, 200),  # 红色攻击粒子
                                    math.cos(angle) * 2,
                                    math.sin(angle) * 2,
                                    20, 3, 0.9, 0
                                )
                            
                            # 如果怪物死亡，获得经验值
                            if not monster.is_alive:
                                player_exp += monster.exp_reward
                                # 随机掉落更好的武器
                                if random.random() < 0.2:  # 20%的概率掉落武器
                                    upgrade_weapon()
                
                # 添加攻击范围视觉效果
                skill_effects.append({
                    "x": player_x,
                    "y": player_y,
                    "range": attack_range,
                    "color": (255, 255, 255),  # 白色攻击范围
                    "timer": 10
                })
            elif event.button == 3:  # 右键：开始拖拽视角
                mouse_dragging = True
                camera_follow_player = False  # 暂停跟随
                last_mouse_x, last_mouse_y = pygame.mouse.get_pos()
                
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 3:  # 右键释放，停止拖拽并恢复跟随（根据用户记忆优化）
                # 无论是否发生拖拽，右键释放时都自动恢复跟随状态
                mouse_dragging = False
                camera_follow_player = True  # 强制恢复跟随状态
                
        elif event.type == pygame.MOUSEMOTION:
            if mouse_dragging:
                # 获取鼠标位置变化
                mouse_x, mouse_y = pygame.mouse.get_pos()
                dx = mouse_x - last_mouse_x
                dy = mouse_y - last_mouse_y
                
                # 移动相机（反向移动实现拖拽效果）
                camera_x -= dx * camera_drag_speed
                camera_y -= dy * camera_drag_speed
                
                # 限制相机范围
                camera_x = max(-WINDOW_WIDTH // 2, min(GAME_WIDTH - WINDOW_WIDTH // 2, camera_x))
                camera_y = max(-WINDOW_HEIGHT // 2, min(GAME_HEIGHT - WINDOW_HEIGHT // 2, camera_y))
                
                # 更新鼠标位置
                last_mouse_x = mouse_x
                last_mouse_y = mouse_y
                
                # 在拖拽时停止跟随玩家（确保拖拽过程中不会自动跟随）
                camera_follow_player = False

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LSHIFT:  # 松开Shift键停止冲刺
                is_dashing = False  # 设置冲刺状态为False

    # 处理玩家移动
    if is_dashing:
        player_speed = player_dash_speed  # 使用冲刺速度
    else:
        player_speed = 12  # 进一步增加基础速度

    # 计算下一个位置
    next_x = player_x + player_velocity_x
    next_y = player_y + player_velocity_y

    # 其他游戏逻辑...

    # 检查是否完成当前关卡
    if len(monsters) == 0:  # 如果没有怪物，表示关卡完成
        current_level_index += 1
        if current_level_index < len(LEVELS):
            load_level(current_level_index)  # 加载下一关卡
        else:
            game_won = True  # 所有关卡完成，游戏胜利

    # 这里移除了重复的子弹更新逻辑，因为在后面已经有了正确的子弹处理代码

    # 其他游戏逻辑...

    # 如果游戏暂停，跳过更新逻辑
    if game_paused:
        # 只更新显示
        pygame.display.flip()
        clock.tick(60)
        continue

    if not game_won and not game_over:
        # Get key state
        keys = pygame.key.get_pressed()
        
        # Calculate next position with acceleration
        acceleration_x = 0
        acceleration_y = 0
        
        # 第一个玩家使用WASD键或方向键
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            acceleration_x -= player_acceleration
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            acceleration_x += player_acceleration
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            acceleration_y -= player_acceleration
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            acceleration_y += player_acceleration

        # 根据移动方向更新玩家朝向
        if acceleration_x != 0 or acceleration_y != 0:
            player_facing_angle = math.atan2(acceleration_y, acceleration_x)
            
        # 按住Shift键加速
        if keys[pygame.K_LSHIFT] and player_dash_cooldown <= 0:
            speed_multiplier = player_dash_speed / player_max_speed
            player_velocity_x *= speed_multiplier
            player_velocity_y *= speed_multiplier
            player_dash_cooldown = DASH_COOLDOWN_MAX
        
        # 更新速度
        player_velocity_x += acceleration_x
        player_velocity_y += acceleration_y
        
        # 应用摩擦力
        player_velocity_x *= player_friction
        player_velocity_y *= player_friction
        
        # 制最大速度
        speed = (player_velocity_x ** 2 + player_velocity_y ** 2) ** 0.5
        if speed > player_max_speed:
            player_velocity_x = player_velocity_x / speed * player_max_speed
            player_velocity_y = player_velocity_y / speed * player_max_speed
        
        # 计算下一个位置
        next_x = player_x + player_velocity_x
        next_y = player_y + player_velocity_y

        # 更新冲刺冷却
        if player_dash_cooldown > 0:
            player_dash_cooldown -= 1
        
        # 计算当前速度（解决speed未定义问题）
        speed = (player_velocity_x ** 2 + player_velocity_y ** 2) ** 0.5

        # 检查是否与迷宫墙壁碰撞（穿墙模式下跳过碰撞检测）
        if no_clip_mode or not check_collision_with_maze(next_x, next_y, player_size, maze):
            player_x = next_x
            player_y = next_y
        else:
            # 尝试只在x或y方向移动
            if not check_collision_with_maze(next_x, player_y, player_size, maze):
                player_x = next_x
            elif not check_collision_with_maze(player_x, next_y, player_size, maze):
                player_y = next_y
            # 如果两个方向都不能移动，玩家保持原位
            player_velocity_x = 0
            player_velocity_y = 0
        
        # 确保玩家不会超出游戏边界
        player_x = max(player_size // 2, min(GAME_WIDTH - player_size // 2, player_x))
        player_y = max(player_size // 2, min(GAME_HEIGHT - player_size // 2, player_y))

        # 更新相机位置（跟随玩家或鼠标拖拽控制）
        if camera_follow_player:
            camera_x = player_x - WINDOW_WIDTH // 2
            camera_y = player_y - WINDOW_HEIGHT // 2
            # 限制相机位置不超出游戏边界
            camera_x = max(-WINDOW_WIDTH // 2, min(GAME_WIDTH - WINDOW_WIDTH // 2, camera_x))
            camera_y = max(-WINDOW_HEIGHT // 2, min(GAME_HEIGHT - WINDOW_HEIGHT // 2, camera_y))

        # 优化的怪物更新系统
        alive_monsters = []
        for monster in monsters:
            if monster.is_alive:
                # 只更新视野范围内的怪物
                if is_in_view(monster.x, monster.y, camera_x, camera_y):
                    monster.move_towards_player(player_x, player_y, maze)
                elif ((monster.x - player_x) ** 2 + (monster.y - player_y) ** 2) < (CELL_SIZE * 8) ** 2:
                    # 在追踪范围内但不在视野内的怪物，使用简化更新
                    monster.move_towards_player(player_x, player_y, None)  # 不传递迷宫以减少计算
                
                monster.update_attack_cooldown()
                alive_monsters.append(monster)
        
        monsters = alive_monsters
        
        # 处理怪物刷新
        if len(monsters) < MIN_MONSTERS and monster_spawn_timer <= 0:
            # 计算需刷新的怪物数量
            spawn_count = min(MAX_MONSTERS - len(monsters), 
                              random.randint(1, 2))  # 每次新1-2个怪物
            # 生成新怪物
            new_monsters = generate_monsters(spawn_count)
            monsters.extend(new_monsters)
            monster_spawn_timer = MONSTER_SPAWN_COOLDOWN  # 刷新冷却时间
            
        # 更新刷新计时器
        if monster_spawn_timer > 0:
            monster_spawn_timer -= 1

        # 处理怪物主动攻击玩家（不需要碰撞）
        if combat_cooldown > 0:
            combat_cooldown -= 1
            
        # 怪物主动攻击逻辑
        for monster in monsters:
            # 攻击第一个玩家
            if monster.can_attack_player(player_x, player_y) and monster.is_alive:
                if monster.attack_player(player_x, player_y):
                    # 怪物攻击玩家
                    if not player_invincible:  # 检查玩家是否无敌
                        damage = max(monster.attack - player_defense, 0)
                        player_hp -= damage
                        player_is_hit = True
                        player_hit_timer = 30  # 闪烁持续30帧
                        
                        # 添加攻击特效
                        for _ in range(10):
                            angle = random.uniform(0, math.pi * 2)
                            particle_system.add_particle(
                                player_x + random.uniform(-10, 10),
                                player_y + random.uniform(-10, 10),
                                (255, 0, 0, 200),  # 红色攻击粒子
                                math.cos(angle) * 2,
                                math.sin(angle) * 2,
                                20, 3, 0.9, 0
                            )
                    
                    if player_hp <= 0:
                        game_over = True
                        break

        # 处理回血包
        for health_pack in health_packs:
            if health_pack.active and health_pack.check_collision(player_x, player_y, player_size):
                player_hp = min(player_hp + HEALTH_RESTORE_AMOUNT, player_max_hp)
                health_pack.active = False
        
        # 清理已使用的回血包
        health_packs = [hp for hp in health_packs if hp.active]
        
        # 处理回血包刷新
        if len(health_packs) < MAX_HEALTH_PACKS and health_pack_spawn_timer <= 0:
            spawn_count = min(MAX_HEALTH_PACKS - len(health_packs), 
                              random.randint(1, 2))  # 每次刷新1-2个回血包
            new_health_packs = generate_health_packs(spawn_count)
            health_packs.extend(new_health_packs)
            health_pack_spawn_timer = HEALTH_PACK_SPAWN_COOLDOWN
        
        # 更新回血包刷新计时器
        if health_pack_spawn_timer > 0:
            health_pack_spawn_timer -= 1

        # 技能触发检测
        for skill_name, skill in SKILLS.items():
            if keys[skill["key"]] and player_skills_cooldown[skill_name] <= 0:
                if skill_name == "Area Attack":
                    # 范围攻击 - 触发挥剑效果
                    weapon_is_swinging = True
                    weapon_swing_timer = WEAPON_SWING_DURATION

                    # 对范围内敌人造成伤害
                    attack_range = skill["range"]
                    for monster in monsters:
                        if monster.is_alive:
                            distance = ((player_x - monster.x) ** 2 + (player_y - monster.y) ** 2) ** 0.5
                            if distance <= attack_range:
                                monster.take_damage(skill["damage"])
                                # 添加攻击特效
                                for _ in range(10):
                                    angle = random.uniform(0, math.pi * 2)
                                    particle_system.add_particle(
                                        monster.x + random.uniform(-10, 10),
                                        monster.y + random.uniform(-10, 10),
                                        (255, 255, 100, 200),
                                        math.cos(angle) * 2,
                                        math.sin(angle) * 2,
                                        20, 3, 0.9, 0
                                    )
                                if not monster.is_alive:
                                    player_exp += monster.exp_reward

                    # 添加范围攻击视觉效果
                    skill_effects.append({
                        "x": player_x,
                        "y": player_y,
                        "range": attack_range,
                        "color": skill["color"],
                        "timer": 15
                    })

                elif skill_name == "Heal":
                    # 治疗效果
                    player_hp = min(player_hp + skill["heal"], player_max_hp)
                    # 添加治疗粒子效果
                    for _ in range(20):
                        angle = random.uniform(0, math.pi * 2)
                        distance = random.uniform(10, 40)
                        particle_system.add_particle(
                            player_x + math.cos(angle) * distance,
                            player_y + math.sin(angle) * distance,
                            (0, 255, 0, 200),  # 绿色粒子
                            math.cos(angle) * 1.5,
                            math.sin(angle) * 1.5,
                            30, 3, 0.95, 0
                        )
                    skill_effects.append({
                        "x": player_x,
                        "y": player_y,
                        "range": 50,
                        "color": skill["color"],
                        "timer": 30
                    })
                
                elif skill_name == "Flash":
                    # 闪现效果
                    # 添加闪现粒子效果
                    for _ in range(30):
                        particle_system.add_particle(
                            player_x, player_y,
                            (200, 200, 255, 200),  # 蓝白色粒子
                            random.uniform(-2, 2),
                            random.uniform(-2, 2),
                            20, 2, 0.9, 0
                        )
                    angle = math.atan2(next_y - player_y, next_x - player_x)
                    flash_x = player_x + math.cos(angle) * skill["distance"]
                    flash_y = player_y + math.sin(angle) * skill["distance"]
                    
                    # 检查闪现目标位置是否有效 - 完善边界检查
                    cell_x = int(flash_x) // CELL_SIZE
                    cell_y = int(flash_y) // CELL_SIZE
                    
                    # 确保不会闪现到地图外（使用迷宫的格子数量）
                    cell_x = max(0, min(cell_x, MAZE_WIDTH - 1))
                    cell_y = max(0, min(cell_y, MAZE_HEIGHT - 1))
                    
                    # 双重检查确保不越界
                    if (0 <= cell_y < len(maze) and 0 <= cell_x < len(maze[0]) and 
                        cell_y < MAZE_HEIGHT and cell_x < MAZE_WIDTH and
                        maze[cell_y][cell_x] == 0):
                        # 确保闪现的位置在格中心
                        player_x = cell_x * CELL_SIZE + CELL_SIZE//2
                        player_y = cell_y * CELL_SIZE + CELL_SIZE//2
                        skill_effects.append({
                            "x": player_x,
                            "y": player_y,
                            "range": 30,
                            "color": skill["color"],
                            "timer": 20
                        })
                
                elif skill_name == "Invincible":
                    # 无敌效果
                    player_invincible = True
                    player_invincible_timer = skill["duration"]
                    skill_effects.append({
                        "x": player_x,
                        "y": player_y,
                        "range": 40,
                        "color": skill["color"],
                        "timer": skill["duration"]
                    })
                
                elif skill_name == "Multi Shot":
                    # 多重射击效果（来自枪战.py的R键技能）
                    # 获取鼠标位置作为射击方向
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    world_mouse_x = mouse_x + camera_x
                    world_mouse_y = mouse_y + camera_y
                    
                    # 计算射击角度
                    dx = world_mouse_x - player_x
                    dy = world_mouse_y - player_y
                    base_angle = math.atan2(dy, dx)
                    
                    # 发射多颗子弹
                    bullet_count = skill["bullet_count"]
                    for i in range(bullet_count):
                        spread_angle = (i * (0 / bullet_count)) * (math.pi / 180)  # 均匀分布在360度
                        bullet_speed = 15
                        bullet_dx = math.cos(spread_angle) * bullet_speed
                        bullet_dy = math.sin(spread_angle) * bullet_speed
                        
                        # 添加子弹到列表：[x, y, dx, dy, damage, lifetime]
                        player_bullets.append([
                            player_x, player_y, 
                            bullet_dx, bullet_dy,
                            skill["damage"], 120  # 2秒生命周期
                        ])
                    
                    # 添加金色粒子特效
                    for _ in range(50):
                        angle = random.uniform(0, 2 * math.pi)
                        speed = random.uniform(2, 5)
                        particle_system.add_particle(
                            player_x, player_y,
                            skill["color"] + (200,),  # 添加alpha通道
                            math.cos(angle) * speed,
                            math.sin(angle) * speed,
                            60, random.randint(3, 6), 0.95, 0
                        )
                    
                    # 添加技能特效
                    skill_effects.append({
                        "x": player_x,
                        "y": player_y,
                        "range": 80,
                        "color": skill["color"],
                        "timer": 60
                    })
                
                player_skills_cooldown[skill_name] = skill["cooldown"]
        
        # 更新技能冷却和特效
        for skill_name in player_skills_cooldown:
            if player_skills_cooldown[skill_name] > 0:
                player_skills_cooldown[skill_name] -= 1
        
        # 更新无敌状态
        if player_invincible_timer > 0:
            player_invincible_timer -= 1
            if player_invincible_timer <= 0:
                player_invincible = False
        
        # 更新技能特效
        skill_effects = [effect for effect in skill_effects if effect["timer"] > 0]
        for effect in skill_effects:
            effect["timer"] -= 1
        
        # 更新子弹
        for bullet in player_bullets[:]:
            # 更新子弹位置
            bullet[0] += bullet[2]  # x += dx
            bullet[1] += bullet[3]  # y += dy
            bullet[5] -= 1  # 减少生命周期
            
            # 移除超出边界或生命周期结束的子弹
            if (bullet[0] < 0 or bullet[0] > GAME_WIDTH or 
                bullet[1] < 0 or bullet[1] > GAME_HEIGHT or 
                bullet[5] <= 0):
                player_bullets.remove(bullet)
                continue
            
            # 检查子弹是否击中怪物
            for monster in monsters[:]:
                if monster.is_alive:
                    distance = ((bullet[0] - monster.x) ** 2 + (bullet[1] - monster.y) ** 2) ** 0.5
                    if distance < monster.size // 2:
                        # 对怪物造成伤害
                        monster.take_damage(bullet[4])  # bullet[4] 是伤害值
                        
                        # 添加击中特效
                        for _ in range(5):
                            angle = random.uniform(0, math.pi * 2)
                            particle_system.add_particle(
                                monster.x + random.uniform(-10, 10),
                                monster.y + random.uniform(-10, 10),
                                (255, 100, 100, 200),  # 红色伤害粒子
                                math.cos(angle) * 2,
                                math.sin(angle) * 2,
                                15, 3, 0.9, 0
                            )
                        
                        # 移除子弹
                        if bullet in player_bullets:
                            player_bullets.remove(bullet)
                        
                        # 检查怪物是否死亡
                        if not monster.is_alive:
                            # 添加经验值
                            player_exp += monster.exp_reward
                            # 检查是否升级
                            while player_exp >= player_exp_to_next_level:
                                player_level += 1
                                player_exp -= player_exp_to_next_level
                                player_exp_to_next_level = int(player_exp_to_next_level * 1.2)
                                player_max_hp += 20
                                player_hp = player_max_hp
                                player_base_attack += 5
                                player_defense += 2
                                player_attack = player_base_attack + player_weapon.attack_bonus
                        break

    # Drawing
    window.fill(BLACK)

    # Draw background
    pygame.draw.rect(window, (30, 30, 30), (0, 0, WINDOW_WIDTH, WINDOW_HEIGHT))
    
    # 绘制迷宫
    draw_maze(window, maze, camera_x, camera_y)
    
    # Draw game border
    border_color = (50, 50, 50)
    border_width = 5
    pygame.draw.rect(window, border_color, 
                     (-camera_x, -camera_y, GAME_WIDTH, GAME_HEIGHT), 
                     border_width)

    # 只渲染视野范围内的对象
    for monster in monsters:
        if is_in_view(monster.x, monster.y, camera_x, camera_y):
            monster.draw(window, camera_x, camera_y)

    # 判断玩家朝向（四个方向：右、左、上、下）
    angle_deg = math.degrees(player_facing_angle)
    # 归一化到 -180 到 180
    while angle_deg > 180:
        angle_deg -= 360
    while angle_deg < -180:
        angle_deg += 360

    # 确定朝向：右(-45~45), 下(45~135), 左(135~180 or -180~-135), 上(-135~-45)
    if -45 <= angle_deg <= 45:
        player_direction = "right"
    elif 45 < angle_deg <= 135:
        player_direction = "down"
    elif angle_deg > 135 or angle_deg < -135:
        player_direction = "left"
    else:
        player_direction = "up"

    # 绘制玩家
    if not player_is_hit or (player_hit_timer // 3) % 2 == 0:
        if player_image:
            # 根据朝向翻转/显示图片
            if player_direction == "left":
                display_player = pygame.transform.flip(player_image, True, False)
            else:
                display_player = player_image
            player_rect = display_player.get_rect(center=(player_x - camera_x, player_y - camera_y))
            window.blit(display_player, player_rect)
        else:
            # 备用：绘制玩家本体（黄色圆形）
            pygame.draw.circle(window, YELLOW,
                             (player_x - camera_x, player_y - camera_y),
                             player_size // 2)

    # 绘制武器（握在手里，只有左右方向）
    screen_player_x = player_x - camera_x
    screen_player_y = player_y - camera_y

    # 武器挥动动画更新
    if weapon_is_swinging:
        weapon_swing_timer -= 1
        swing_progress = 1 - (weapon_swing_timer / WEAPON_SWING_DURATION)
        # 挥动角度从+60度到-60度（从上往下挥）
        weapon_swing_angle = 60 - swing_progress * 120
        if weapon_swing_timer <= 0:
            weapon_is_swinging = False
            weapon_swing_angle = 0

    # 判断朝左还是朝右（只有左右两个方向）
    facing_left = player_direction == "left" or player_direction == "up"  # 上也算左

    # 手的位置（紧贴角色边缘）
    hand_offset_x = player_size // 2 - 10  # 手在角色边缘内侧
    hand_offset_y = 2  # 手稍微偏下

    if facing_left:
        hand_x = screen_player_x - hand_offset_x
        hand_y = screen_player_y + hand_offset_y
    else:
        hand_x = screen_player_x + hand_offset_x
        hand_y = screen_player_y + hand_offset_y

    # 武器参数
    weapon_half_size = 16  # 武器图片一半大小
    default_angle = -45  # 默认向上倾斜45度（朝右时为右上，即指向右上方）

    # 朝右时的角度计算（基准）
    # actual_angle: 剑指向的实际角度（从手出发）
    # 默认-45度（右上），挥动时从+15度到-105度
    right_actual_angle = default_angle + weapon_swing_angle

    if weapon_image_original:
        if facing_left:
            # 朝左：完全镜像朝右的效果
            # 水平镜像图片
            weapon_img = pygame.transform.flip(weapon_image_original, True, False)
            # 镜像角度计算：X轴镜像，角度变为 180 - angle
            # 朝右-45度（右上） -> 朝左225度（左上） = 180 - (-45) = 225
            actual_angle = 180 - right_actual_angle
            # 图片旋转角度：因为图片已经水平翻转，需要调整旋转
            # 原始图片假设剑尖朝右下(-45度方向)，翻转后剑尖朝左下
            # 要让翻转后的剑指向actual_angle方向
            rot_angle = -(actual_angle - 180) - 45
        else:
            # 朝右
            weapon_img = weapon_image_original
            actual_angle = right_actual_angle
            # 原始图片剑尖朝右下，旋转使其指向actual_angle
            rot_angle = -actual_angle - 45

        # 旋转武器
        rotated_weapon = pygame.transform.rotate(weapon_img, rot_angle)

        # 武器中心相对于手的偏移（让剑柄在手上，剑身向外延伸）
        angle_rad = math.radians(actual_angle)
        offset_x = math.cos(angle_rad) * weapon_half_size
        offset_y = math.sin(angle_rad) * weapon_half_size

        weapon_center_x = hand_x + offset_x
        weapon_center_y = hand_y + offset_y

        weapon_rect = rotated_weapon.get_rect(center=(weapon_center_x, weapon_center_y))
        window.blit(rotated_weapon, weapon_rect)
    else:
        # 备用：绘制简单的武器线条（以手为轴心）
        weapon_length = 22
        if facing_left:
            actual_angle = 180 - right_actual_angle
        else:
            actual_angle = right_actual_angle
        angle_rad = math.radians(actual_angle)
        weapon_end_x = hand_x + math.cos(angle_rad) * weapon_length
        weapon_end_y = hand_y + math.sin(angle_rad) * weapon_length
        # 剑身
        pygame.draw.line(window, (192, 192, 192),
                        (int(hand_x), int(hand_y)),
                        (int(weapon_end_x), int(weapon_end_y)), 3)

    # Draw health packs
    for health_pack in health_packs:
        health_pack.draw(window, camera_x, camera_y)
    
    # 绘制子弹
    for bullet in player_bullets:
        screen_x = bullet[0] - camera_x
        screen_y = bullet[1] - camera_y
        
        # 绘制子弹主体
        pygame.draw.circle(window, (255, 255, 0),  # 黄色子弹
                          (int(screen_x), int(screen_y)), 4)
        
        # 添加子弹光晕效果
        glow_surface = pygame.Surface((16, 16), pygame.SRCALPHA)
        for radius in range(8, 0, -2):
            alpha = int(100 * (radius / 8))
            pygame.draw.circle(glow_surface, (255, 255, 100, alpha),
                             (8, 8), radius)
        window.blit(glow_surface, (int(screen_x) - 8, int(screen_y) - 8))

    # 绘制战争迷雾效果（只在玩家周围光圈范围内显示内容）
    if FOG_OF_WAR_ENABLED:
        # 创建一个全屏的黑色表面
        fog_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        fog_surface.fill((0, 0, 0, 200))  # 半透明黑色
        
        # 在玩家视野范围内创建一个透明圆形区域
        player_screen_x = player_x - camera_x
        player_screen_y = player_y - camera_y
        
        # 创建视野圆形区域（透明）
        pygame.draw.circle(fog_surface, (0, 0, 0, 0), 
                          (int(player_screen_x), int(player_screen_y)), 
                          VISIBILITY_RADIUS)
        
        # 将迷雾表面绘制到窗口上
        window.blit(fog_surface, (0, 0))

    # 更新相机位置
    camera.update(camera_x, camera_y)

    # 绘制粒子效果
    particle_system.draw(window, camera)

    # 绘制光照效果（在UI之前绘制）
    lighting_system.draw(window, camera)

    # Draw game over message
    if game_over:
        text = FONT_TITLE.render('游戏结束! 按R复活', True, RED)
        text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        window.blit(text, text_rect)

        pygame.display.flip()
        clock.tick(60)
        continue

    # 优化的UI显示系统
    font = FONT_LARGE
    font_small = FONT_SMALL

    # 生命值显示（添加颜色反馈）
    hp_color = GREEN if player_hp > player_max_hp * 0.6 else YELLOW if player_hp > player_max_hp * 0.3 else RED
    hp_text = font.render(f'生命: {player_hp}/{player_max_hp}', True, hp_color)
    window.blit(hp_text, (10, 8))

    # 生命值条
    hp_bar_width = 150
    hp_bar_height = 12
    hp_percentage = player_hp / player_max_hp
    pygame.draw.rect(window, (60, 60, 60), (10, 28, hp_bar_width, hp_bar_height))  # 背景
    pygame.draw.rect(window, hp_color, (10, 28, hp_bar_width * hp_percentage, hp_bar_height))  # 当前血量
    pygame.draw.rect(window, WHITE, (10, 28, hp_bar_width, hp_bar_height), 1)  # 边框

    level_offset = 48

    # 等级和免疫力显示
    level_text = font_small.render(f'等级: {player_level}  免疫力: {player_exp}/{player_exp_to_next_level}', True, WHITE)
    window.blit(level_text, (10, level_offset))

    # 免疫力条
    exp_bar_width = 150
    exp_bar_height = 8
    exp_percentage = player_exp / player_exp_to_next_level
    exp_bar_y = level_offset + 18
    pygame.draw.rect(window, (40, 40, 40), (10, exp_bar_y, exp_bar_width, exp_bar_height))  # 背景
    pygame.draw.rect(window, GOLD, (10, exp_bar_y, exp_bar_width * exp_percentage, exp_bar_height))  # 当前免疫力
    pygame.draw.rect(window, WHITE, (10, exp_bar_y, exp_bar_width, exp_bar_height), 1)  # 边框

    # 武器信息
    weapon_y = exp_bar_y + 14
    weapon_text = font_small.render(f'武器: {player_weapon.name}  攻击: {player_attack}', True, YELLOW)
    window.blit(weapon_text, (10, weapon_y))

    # Draw skill effects
    for effect in skill_effects:
        effect_alpha = int(255 * (effect["timer"] / 30))
        effect_surface = pygame.Surface((effect["range"] * 2, effect["range"] * 2), pygame.SRCALPHA)
        
        # 获取基础颜色并确保是RGB格式
        base_color = effect["color"]
        # 确保effect_alpha在有效范围内
        effect_alpha = max(0, min(255, effect_alpha))
        if len(base_color) == 3:  # RGB格式
            color_with_alpha = list(base_color) + [effect_alpha]  # 添加alpha通道
        else:  # 已经是RGBA格式
            color_with_alpha = list(base_color[:3]) + [effect_alpha]  # 替换alpha值
            
        # 确保所有颜色值在有效范围内
        for i in range(len(color_with_alpha)):
            color_with_alpha[i] = max(0, min(255, color_with_alpha[i]))
            
        try:
            pygame.draw.circle(effect_surface, color_with_alpha,
                             (effect["range"], effect["range"]), effect["range"])
            window.blit(effect_surface, 
                       (effect["x"] - effect["range"] - camera_x,
                        effect["y"] - effect["range"] - camera_y))
        except ValueError:
            print(f"Invalid color value: {color_with_alpha}")
            continue

    # 优化的技能冷却显示
    y_offset = 100
    skill_title = font_small.render('技能:', True, WHITE)
    window.blit(skill_title, (10, y_offset))
    y_offset += 18

    # 技能名称中英对照和详细信息
    skill_info_cn = {
        "Area Attack": {
            "name": "范围攻击",
            "desc": lambda s: f"伤害:{s['damage']} 范围:{s['range']}"
        },
        "Heal": {
            "name": "治疗",
            "desc": lambda s: f"恢复:{s['heal']}HP"
        },
        "Flash": {
            "name": "闪现",
            "desc": lambda s: f"距离:{s['distance']}"
        },
        "Invincible": {
            "name": "无敌",
            "desc": lambda s: f"持续:{s['duration']//60}秒"
        },
        "Multi Shot": {
            "name": "多重射击",
            "desc": lambda s: f"伤害:{s['damage']} 子弹:{s['bullet_count']}"
        }
    }

    for skill_name, skill in SKILLS.items():
        # 获取按键名称
        key_name = pygame.key.name(skill["key"]).upper()
        info = skill_info_cn.get(skill_name, {"name": skill_name, "desc": lambda s: ""})
        skill_cn = info["name"]
        skill_desc = info["desc"](skill)
        skill_level = skill.get("level", 1)

        # 显示技能名称、等级和按键
        if player_skills_cooldown[skill_name] > 0:
            cooldown_seconds = player_skills_cooldown[skill_name] // 60 + 1
            status_text = f'{cooldown_seconds}秒'
            status_color = RED
        else:
            status_text = '就绪'
            status_color = GREEN

        # 第一行：按键、名称、等级、状态
        line1 = FONT_TINY.render(f'[{key_name}] {skill_cn} Lv{skill_level}: {status_text}', True, status_color)
        window.blit(line1, (10, y_offset))
        y_offset += 14

        # 第二行：技能详情（较小字体，灰色）
        line2 = FONT_TINY.render(f'    {skill_desc}', True, (180, 180, 180))
        window.blit(line2, (10, y_offset))
        y_offset += 16

    # 冲刺冷却显示
    if player_dash_cooldown > 0:
        dash_text = FONT_TINY.render(f'[SHIFT] 冲刺: {player_dash_cooldown//60 + 1}秒', True, RED)
    else:
        dash_text = FONT_TINY.render('[SHIFT] 冲刺: 就绪', True, GREEN)
    window.blit(dash_text, (10, y_offset))
    y_offset += 16

    # 其他技能/功能显示
    other_skills = [
        {"key": "Q", "name": "滑动攻击", "desc": "向鼠标方向滑动攻击"},
        {"key": "M", "name": "加强", "desc": "攻击+10 速度+2 防御+5"},
        {"key": "L", "name": "穿墙", "desc": f"当前:{'开启' if no_clip_mode else '关闭'}"},
        {"key": "H", "name": "作弊", "desc": "回血+免疫力+升级"},
        {"key": "O", "name": "升级武器", "desc": "提升武器等级"},
        {"key": "K", "name": "降级武器", "desc": "降低武器等级"},
        {"key": "U", "name": "升级技能", "desc": f"消耗{SKILL_UPGRADE_COST}免疫力"},
    ]

    for skill in other_skills:
        line = FONT_TINY.render(f"[{skill['key']}] {skill['name']}: {skill['desc']}", True, (200, 200, 200))
        window.blit(line, (10, y_offset))
        y_offset += 15

    # 小地图显示（右上角）- 显示玩家周围区域
    minimap_size = 120
    minimap_x = WINDOW_WIDTH - minimap_size - 10
    minimap_y = 10
    minimap_range = 800  # 小地图显示的实际游戏范围（像素）

    # 创建小地图表面
    minimap_surface = pygame.Surface((minimap_size, minimap_size), pygame.SRCALPHA)
    minimap_surface.fill((20, 20, 30, 200))  # 半透明深色背景

    # 计算小地图显示区域（以玩家为中心）
    map_left = player_x - minimap_range // 2
    map_top = player_y - minimap_range // 2
    scale = minimap_size / minimap_range

    # 绘制迷宫墙壁（简化显示）
    wall_start_x = max(0, int(map_left // CELL_SIZE))
    wall_end_x = min(MAZE_WIDTH, int((map_left + minimap_range) // CELL_SIZE) + 1)
    wall_start_y = max(0, int(map_top // CELL_SIZE))
    wall_end_y = min(MAZE_HEIGHT, int((map_top + minimap_range) // CELL_SIZE) + 1)

    for y in range(wall_start_y, wall_end_y):
        for x in range(wall_start_x, wall_end_x):
            if maze[y][x] == 1:  # 墙壁
                wall_screen_x = int((x * CELL_SIZE - map_left) * scale)
                wall_screen_y = int((y * CELL_SIZE - map_top) * scale)
                wall_size = max(2, int(CELL_SIZE * scale))
                if 0 <= wall_screen_x < minimap_size and 0 <= wall_screen_y < minimap_size:
                    pygame.draw.rect(minimap_surface, (60, 60, 80),
                                   (wall_screen_x, wall_screen_y, wall_size, wall_size))

    # 绘制怪物（显示范围内的所有怪物）
    for monster in monsters:
        if monster.is_alive:
            mx = int((monster.x - map_left) * scale)
            my = int((monster.y - map_top) * scale)
            if 0 <= mx < minimap_size and 0 <= my < minimap_size:
                color = (255, 100, 100) if monster.is_boss else (255, 80, 80)
                size = 3 if monster.is_boss else 2
                pygame.draw.circle(minimap_surface, color, (mx, my), size)

    # 绘制玩家（始终在中心）
    player_mx = minimap_size // 2
    player_my = minimap_size // 2
    pygame.draw.circle(minimap_surface, (100, 255, 100), (player_mx, player_my), 4)
    pygame.draw.circle(minimap_surface, WHITE, (player_mx, player_my), 4, 1)

    # 绘制小地图到窗口
    window.blit(minimap_surface, (minimap_x, minimap_y))
    pygame.draw.rect(window, (100, 100, 120), (minimap_x, minimap_y, minimap_size, minimap_size), 2)


    # 绘制对话
    player_monster_dialogue.draw(window)

    # 优化的状态显示（底部）
    status_y = WINDOW_HEIGHT - 50

    # 相机状态指示
    if mouse_dragging:
        status_text = FONT_TINY.render("拖拽视角中... | 右键释放恢复跟随", True, GREEN)
    elif camera_follow_player:
        status_text = FONT_TINY.render("跟随模式 | 右键拖拽视角", True, WHITE)
    else:
        status_text = FONT_TINY.render("自由视角 | 右键恢复跟随", True, YELLOW)
    window.blit(status_text, (10, status_y))

    # 攻击控制说明
    attack_text = FONT_TINY.render("左键:近战 | M:加强", True, WHITE)
    window.blit(attack_text, (10, status_y + 16))

    # 游戏统计信息
    alive_monsters = len([m for m in monsters if m.is_alive])
    stats_text = FONT_TINY.render(f"病毒: {alive_monsters}/{MAX_MONSTERS} | 关卡: {current_level_index}", True, GOLD)
    window.blit(stats_text, (10, status_y + 32))

    # ========== 右下角病毒统计面板 ==========
    # 统计各类病毒数量
    virus_counts = {}
    boss_counts = {}
    for monster in monsters:
        if monster.is_alive:
            if monster.is_boss:
                boss_counts[monster.name] = boss_counts.get(monster.name, 0) + 1
            else:
                virus_counts[monster.name] = virus_counts.get(monster.name, 0) + 1

    # 面板尺寸和位置
    panel_width = 180
    panel_height = 200
    panel_x = WINDOW_WIDTH - panel_width - 15
    panel_y = WINDOW_HEIGHT - panel_height - 15

    # 绘制半透明背景面板
    panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
    # 渐变背景效果
    for i in range(panel_height):
        alpha = int(180 - i * 0.3)
        pygame.draw.line(panel_surface, (20, 30, 50, alpha), (0, i), (panel_width, i))

    # 绘制发光边框
    pygame.draw.rect(panel_surface, (100, 200, 255, 150), (0, 0, panel_width, panel_height), 2, border_radius=8)
    pygame.draw.rect(panel_surface, (50, 150, 200, 80), (1, 1, panel_width-2, panel_height-2), 1, border_radius=7)

    # 标题栏
    title_rect = pygame.Rect(0, 0, panel_width, 28)
    pygame.draw.rect(panel_surface, (40, 80, 120, 200), title_rect, border_radius=8)
    pygame.draw.rect(panel_surface, (40, 80, 120, 200), (0, 20, panel_width, 10))  # 补齐下方圆角

    # 标题文字
    title_text = FONT_SMALL.render("病毒统计", True, (100, 220, 255))
    title_x = (panel_width - title_text.get_width()) // 2
    panel_surface.blit(title_text, (title_x, 5))

    # 统计内容起始位置
    content_y = 35
    line_height = 18

    # 总计信息
    total_virus = sum(virus_counts.values())
    total_boss = sum(boss_counts.values())
    total_text = FONT_TINY.render(f"存活: {total_virus + total_boss}", True, (255, 220, 100))
    panel_surface.blit(total_text, (10, content_y))

    killed_text = FONT_TINY.render(f"已消灭: {player_exp // 10}", True, (100, 255, 150))
    panel_surface.blit(killed_text, (100, content_y))
    content_y += line_height + 5

    # 分割线
    pygame.draw.line(panel_surface, (80, 120, 160, 150), (10, content_y), (panel_width - 10, content_y))
    content_y += 8

    # 显示各类病毒（最多显示7种，按数量排序）
    sorted_viruses = sorted(virus_counts.items(), key=lambda x: x[1], reverse=True)[:7]

    # 病毒颜色映射
    virus_colors = {
        "感冒病毒": (100, 200, 100),
        "流感病毒": (255, 150, 50),
        "蛀牙细菌": (200, 200, 180),
        "鼻涕虫菌": (180, 220, 100),
        "肚子疼菌": (139, 90, 43),
        "熬夜菌": (180, 150, 220),
        "咳嗽病毒": (100, 100, 120),
        "懒惰菌": (169, 169, 169),
        "坏情绪菌": (100, 50, 150),
        "发烧病毒": (255, 80, 50),
    }

    for virus_name, count in sorted_viruses:
        if content_y > panel_height - 25:
            break
        # 病毒颜色指示点
        color = virus_colors.get(virus_name, (200, 200, 200))
        pygame.draw.circle(panel_surface, color, (18, content_y + 6), 5)
        pygame.draw.circle(panel_surface, (255, 255, 255, 150), (18, content_y + 6), 5, 1)

        # 病毒名称（截断显示）
        display_name = virus_name[:4] if len(virus_name) > 4 else virus_name
        name_text = FONT_TINY.render(display_name, True, (220, 220, 220))
        panel_surface.blit(name_text, (28, content_y))

        # 数量
        count_text = FONT_TINY.render(f"x{count}", True, color)
        panel_surface.blit(count_text, (panel_width - 40, content_y))

        content_y += line_height

    # 显示Boss（如果有）
    if boss_counts:
        content_y += 3
        pygame.draw.line(panel_surface, (200, 80, 80, 150), (10, content_y), (panel_width - 10, content_y))
        content_y += 5
        for boss_name, count in boss_counts.items():
            if content_y > panel_height - 20:
                break
            # Boss用红色星星标识
            pygame.draw.circle(panel_surface, (255, 50, 50), (18, content_y + 6), 6)
            pygame.draw.circle(panel_surface, (255, 200, 100), (18, content_y + 6), 6, 1)

            display_name = boss_name[:4] if len(boss_name) > 4 else boss_name
            boss_text = FONT_TINY.render(display_name, True, (255, 100, 100))
            panel_surface.blit(boss_text, (28, content_y))

            count_text = FONT_TINY.render(f"x{count}", True, (255, 150, 100))
            panel_surface.blit(count_text, (panel_width - 40, content_y))
            content_y += line_height

    # 绘制面板到窗口
    window.blit(panel_surface, (panel_x, panel_y))

    pygame.display.flip()
    clock.tick(60)

    # 更新玩家受伤计时器
    if player_hit_timer > 0:
        player_hit_timer -= 1 
        if player_hit_timer == 0:
            player_is_hit = False
    
    # 更新粒子系统
    particle_system.update()

    # 更新玩家光源位置
    if player_light_index is not None and player_light_index >= 0:
        lighting_system.update_light(player_light_index, player_x, player_y)

    # 检查玩家是否接近病毒并启动对话
    for monster in monsters:
        if monster.check_collision(player_x, player_y, player_size):
            if not player_monster_dialogue.is_active:
                player_monster_dialogue.start()

# 修复商店类
class Shop:
    def __init__(self):
        self.items = {
            "Health Pack": {"cost": 50, "description": "Restores 50 HP"},
            "Iron Sword": {"cost": 100, "description": "Increases attack by 15"},
            "Steel Sword": {"cost": 200, "description": "Increases attack by 25"},
        }
        self.is_open = False

    def toggle_shop(self):
        """Toggle shop open/close"""
        self.is_open = not self.is_open

    def display_items(self, window):
        """Display shop items"""
        if not self.is_open:
            return

        # Draw shop background
        shop_width = 400
        shop_height = 300
        shop_x = (WINDOW_WIDTH - shop_width) // 2
        shop_y = (WINDOW_HEIGHT - shop_height) // 2

        pygame.draw.rect(window, (50, 50, 50), (shop_x, shop_y, shop_width, shop_height))
        pygame.draw.rect(window, WHITE, (shop_x, shop_y, shop_width, shop_height), 3)

        title_text = FONT_LARGE.render("商店 (按S关闭)", True, WHITE)
        window.blit(title_text, (shop_x + 10, shop_y + 10))

        y_offset = shop_y + 50
        item_index = 1
        for item_name, item_info in self.items.items():
            item_text = f"[{item_index}] {item_name}: {item_info['cost']} 免疫力"
            desc_text = f"    {item_info['description']}"

            color = GREEN if player_exp >= item_info['cost'] else RED
            item_surface = FONT_LARGE.render(item_text, True, color)
            desc_surface = FONT_SMALL.render(desc_text, True, WHITE)

            window.blit(item_surface, (shop_x + 10, y_offset))
            window.blit(desc_surface, (shop_x + 10, y_offset + 30))
            y_offset += 60
            item_index += 1

    def buy_item(self, item_name):
        """Buy an item from the shop"""
        global player_exp, player_hp, player_max_hp, player_weapon, player_attack, health_packs
        
        if item_name in self.items:
            item_cost = self.items[item_name]["cost"]
            if player_exp >= item_cost:
                player_exp -= item_cost
                
                if item_name == "Health Pack":
                    # Restore health directly
                    player_hp = min(player_hp + 50, player_max_hp)
                    return True
                elif item_name == "Iron Sword":
                    if player_weapon.name == "Wooden Sword":
                        player_weapon = Weapon("Iron Sword", WEAPON_TYPES["Iron Sword"]["attack"], WEAPON_TYPES["Iron Sword"]["color"])
                        player_attack = player_base_attack + player_weapon.attack_bonus
                        return True
                elif item_name == "Steel Sword":
                    if player_weapon.name in ["Wooden Sword", "Iron Sword"]:
                        player_weapon = Weapon("Steel Sword", WEAPON_TYPES["Steel Sword"]["attack"], WEAPON_TYPES["Steel Sword"]["color"])
                        player_attack = player_base_attack + player_weapon.attack_bonus
                        return True
                        
        return False

# 在游戏主循环中添加售卖机逻辑
shop = Shop()

while running:
    # 事件处理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:  # 按S键打开售卖机
                shop.display_items(window)
            elif event.key == pygame.K_1:  # 购买健康包
                if shop.buy_item("Health Pack", ):
                    print("购买成功：健康包")
                else:
                    print("购买失败：免疫力不足")
            elif event.key == pygame.K_2:  # 购买铁剑
                if shop.buy_item("Iron Sword", ):
                    print("购买成功：铁剑")
                else:
                    print("购买失败：免疫力不足")
            elif event.key == pygame.K_3:  # 购买钢剑
                if shop.buy_item("Steel Sword", ):
                    print("购买成功：钢剑")
                else:
                    print("购买失败：免疫力不足")

    # 其他游戏逻辑...

    # 绘制对话
    player_monster_dialogue.draw(window)
    
    # 绘制商店
    shop.display_items(window)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()