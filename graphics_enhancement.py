import pygame
import random
import math
import time

# 导入Player类以便类型检查
class Player:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.size = 30
        self.speed = 5
        self.health = 100
        self.max_health = 100
        self.bullets = []
        self.last_damage_time = 0
        self.regen_delay = 5
        self.regen_rate = 1
        self.last_regen_time = 0
        self.shoot_cooldown = 0
        self.shoot_delay = 0.1
        self.rapid_fire_active = False
        self.normal_shoot_delay = 0.1
        self.rapid_shoot_delay = 0.05
        self.slow_active = False
        self.slow_end_time = 0
        self.slow_cooldown = 0
        self.velocity_x = 0
        self.velocity_y = 0
        self.dash_active = False
        self.charge_effects = []
        self.charging = False
        self.charge_start_time = 0
        self.max_charge_time = 2.0
        self.stance_active = False
        self.stance_end_time = 0
        self.stance_cooldown = 0
        self.shield_active = False
        self.shield_end_time = 0
        self.shield_cooldown = 0
        self.explosion_cooldown = 0
        self.effects = []
        self.spread_cooldown = 0
        self.spread_delay = 0.1
        self.melee_damage = 15
        self.melee_range = 40
        self.melee_cooldown = 0
        self.melee_delay = 1.0
        self.screen_shake = ScreenShake()
        self.flash_cooldown = 0  # 添加闪现技能冷却时间

# 粒子效果系统
class ParticleSystem:
    def __init__(self):
        self.particles = []
        self.max_particles = 1000  # 限制最大粒子数量
        self.particle_pool = [{'active': False} for _ in range(self.max_particles)]  # 粒子对象池
    
    def add_particle(self, x, y, color, velocity_x=0, velocity_y=0, lifetime=30, size=3, decay=0.95, gravity=0.1):
        # 检查是否达到最大粒子数量
        if len(self.particles) >= self.max_particles:
            return
            
        # 从对象池中获取一个未使用的粒子
        for particle in self.particle_pool:
            if not particle.get('active', False):
                particle.update({
                    'active': True,
                    'x': x,
                    'y': y,
                    'color': color,
                    'velocity_x': velocity_x,
                    'velocity_y': velocity_y,
                    'lifetime': lifetime,
                    'max_lifetime': lifetime,
                    'size': size,
                    'decay': decay,
                    'gravity': gravity
                })
                self.particles.append(particle)
                break
    
    def add_explosion(self, x, y, color, particle_count=20, max_speed=3):
        for _ in range(particle_count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1, max_speed)
            velocity_x = math.cos(angle) * speed
            velocity_y = math.sin(angle) * speed
            lifetime = random.randint(20, 40)
            size = random.uniform(1, 4)
            self.add_particle(x, y, color, velocity_x, velocity_y, lifetime, size)
    
    def add_hit_effect(self, x, y, color):
        for _ in range(10):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(0.5, 2)
            velocity_x = math.cos(angle) * speed
            velocity_y = math.sin(angle) * speed
            lifetime = random.randint(10, 20)
            size = random.uniform(1, 3)
            self.add_particle(x, y, color, velocity_x, velocity_y, lifetime, size, 0.9)
    
    def add_trail(self, x, y, color, direction, speed=1):
        for _ in range(3):
            offset_x = random.uniform(-3, 3)
            offset_y = random.uniform(-3, 3)
            velocity_x = -math.cos(direction) * speed * random.uniform(0.1, 0.5)
            velocity_y = -math.sin(direction) * speed * random.uniform(0.1, 0.5)
            lifetime = random.randint(5, 15)
            size = random.uniform(1, 2)
            self.add_particle(x + offset_x, y + offset_y, color, velocity_x, velocity_y, lifetime, size, 0.85)
    
    def update(self):
        i = len(self.particles) - 1
        while i >= 0:
            particle = self.particles[i]
            if particle['lifetime'] <= 0:
                particle['active'] = False  # 标记为未使用
                self.particles.pop(i)
            else:
                # 批量更新粒子状态
                particle['x'] += particle['velocity_x']
                particle['y'] += particle['velocity_y']
                particle['velocity_y'] += particle['gravity']
                particle['velocity_x'] *= particle['decay']
                particle['velocity_y'] *= particle['decay']
                particle['lifetime'] -= 1
            i -= 1
    
    def draw(self, screen, camera):
        for particle in self.particles:
            alpha = int(255 * (particle['lifetime'] / particle['max_lifetime']))
            # 确保alpha值在有效范围内
            alpha = max(0, min(255, alpha))
            color = list(particle['color'])
            if len(color) == 3:
                color.append(alpha)
            else:
                color[3] = alpha
            
            # 确保颜色值在有效范围内
            for i in range(len(color)):
                color[i] = max(0, min(255, color[i]))
            
            screen_x, screen_y = camera.apply(particle['x'], particle['y'])
            
            # 创建一个临时surface来绘制带透明度的粒子
            particle_surface = pygame.Surface((particle['size'] * 2, particle['size'] * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, color, (particle['size'], particle['size']), particle['size'])
            screen.blit(particle_surface, (screen_x - particle['size'], screen_y - particle['size']))

# 光照效果系统
class LightingSystem:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.lights = []
        self.ambient_light = (180, 180, 200)  # 进一步提高环境光亮度
        self.last_frame_time = time.time()  # 初始化帧率限制计时器
        self.gradient_cache = {}  # 初始化渐变缓存字典
    
    def add_light(self, x, y, radius, color, intensity=1.0):
        self.lights.append({
            'x': x,
            'y': y,
            'radius': radius * 1.2,  # 适中的光照半径
            'color': color,
            'intensity': intensity * 0.3  # 大幅降低光照强度，避免遮挡角色
        })
        return len(self.lights) - 1  # 返回光源索引
    
    def update_light(self, index, x, y):
        if 0 <= index < len(self.lights):
            self.lights[index]['x'] = x
            self.lights[index]['y'] = y
    
    def _create_gradient_surface(self, light):
        light_radius = int(light['radius'])
        cache_key = (light_radius, light['intensity'], str(light['color']))
        
        if cache_key in self.gradient_cache:
            return self.gradient_cache[cache_key]
        
        gradient_surface = pygame.Surface((light_radius * 2, light_radius * 2), pygame.SRCALPHA)
        step_size = max(1, light_radius // 30)  # 根据半径动态调整步长
        
        base_color = light['color']
        if not isinstance(base_color, (tuple, list)) or len(base_color) < 3:
            base_color = (255, 255, 255)
        
        r = max(0, min(255, int(base_color[0])))
        g = max(0, min(255, int(base_color[1])))
        b = max(0, min(255, int(base_color[2])))
        
        for radius in range(light_radius, 0, -step_size):
            progress = radius / light_radius
            alpha = int(255 * (1 - progress ** 2) * light['intensity'])
            alpha = max(0, min(255, alpha))
            color = (r, g, b, alpha)
            
            pygame.draw.circle(gradient_surface, color, (light_radius, light_radius), radius)
        
        self.gradient_cache[cache_key] = gradient_surface
        return gradient_surface

    def draw(self, screen, camera, exclude_rect=None):
        """
        绘制光照效果
        exclude_rect: 可选的排除区域(x, y, width, height)，该区域不会被光照影响（用于UI）
        """
        # 使用缓存的光照表面
        if not hasattr(self, 'cached_light_surface'):
            self.cached_light_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            self.last_lights_positions = {}
            self.last_camera_pos = (0, 0)

        # 检查光源位置或相机是否发生变化
        lights_changed = False
        current_positions = {}
        current_camera = (camera.x, camera.y)

        if current_camera != self.last_camera_pos:
            lights_changed = True
            self.last_camera_pos = current_camera

        for i, light in enumerate(self.lights):
            current_positions[i] = (light['x'], light['y'])
            if i not in self.last_lights_positions or \
               abs(self.last_lights_positions[i][0] - light['x']) > 5 or \
               abs(self.last_lights_positions[i][1] - light['y']) > 5:
                lights_changed = True

        if lights_changed:
            self.cached_light_surface.fill((*self.ambient_light, 40))  # 降低环境光透明度

            visible_lights = [light for light in self.lights if self._is_light_visible(light, camera)]

            for light in visible_lights:
                screen_x, screen_y = camera.apply(light['x'], light['y'])
                gradient_surface = self._create_gradient_surface(light)
                light_radius = int(light['radius'])
                self.cached_light_surface.blit(gradient_surface,
                                              (screen_x - light_radius, screen_y - light_radius),
                                              special_flags=pygame.BLEND_RGBA_MAX)

            self.last_lights_positions = current_positions.copy()

        # 创建一个临时表面用于绘制，排除UI区域
        if exclude_rect:
            temp_surface = self.cached_light_surface.copy()
            # 将UI区域设为透明（不受光照影响）
            pygame.draw.rect(temp_surface, (255, 255, 255, 255), exclude_rect)
            screen.blit(temp_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        else:
            screen.blit(self.cached_light_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        
        # 清理过期的缓存
        if len(self.gradient_cache) > 100:  # 限制缓存大小
            self.gradient_cache.clear()
    
    def _is_light_visible(self, light, camera):
        screen_x, screen_y = camera.apply(light['x'], light['y'])
        return (-light['radius'] <= screen_x <= self.screen_width + light['radius'] and
                -light['radius'] <= screen_y <= self.screen_height + light['radius'])

# 屏幕抖动效果
class ScreenShake:
    def __init__(self):
        self.intensity = 0
        self.duration = 0
    
    def start_shake(self, intensity=5, duration=10):
        self.intensity = intensity
        self.duration = duration
    
    def update(self):
        if self.duration > 0:
            self.duration -= 1
            if self.duration <= 0:
                self.intensity = 0
    
    def get_offset(self):
        if self.duration > 0:
            dx = random.uniform(-self.intensity, self.intensity)
            dy = random.uniform(-self.intensity, self.intensity)
            return dx, dy
        return 0, 0

# 高级渲染函数
def draw_entity_enhanced(screen, entity, camera, particle_system=None):
    screen_x, screen_y = camera.apply(entity.x, entity.y)
    
    # 绘制阴影
    shadow_surface = pygame.Surface((entity.size, entity.size//2), pygame.SRCALPHA)
    shadow_color = (0, 0, 0, 100)  # 半透明黑色
    pygame.draw.ellipse(shadow_surface, shadow_color, (0, 0, entity.size, entity.size//2))
    screen.blit(shadow_surface, (screen_x - entity.size//2, screen_y + entity.size//4))
    
    # 根据实体类型选择不同的渲染方式
    if hasattr(entity, 'type') and entity.type == "分裂":
        # 分裂敌人使用圆形
        entity_surface = pygame.Surface((entity.size, entity.size), pygame.SRCALPHA)
        pygame.draw.circle(entity_surface, entity.color, (entity.size//2, entity.size//2), entity.size//2)
        
        # 添加高光效果
        highlight_pos = (entity.size//4, entity.size//4)
        highlight_size = entity.size//6
        pygame.draw.circle(entity_surface, (255, 255, 255, 150), highlight_pos, highlight_size)
        
        screen.blit(entity_surface, (screen_x - entity.size//2, screen_y - entity.size//2))
    elif hasattr(entity, 'type') and entity.type == "疾速":
        # 疾速敌人使用菱形
        points = [
            (screen_x, screen_y - entity.size//2),  # 上
            (screen_x + entity.size//2, screen_y),  # 右
            (screen_x, screen_y + entity.size//2),  # 下
            (screen_x - entity.size//2, screen_y)   # 左
        ]
        pygame.draw.polygon(screen, entity.color, points)
        
        # 添加速度线
        if particle_system and random.random() < 0.3:  # 30%几率生成拖尾
            for _ in range(2):
                offset = random.uniform(-entity.size/4, entity.size/4)
                particle_system.add_particle(
                    entity.x - math.cos(0) * entity.size/2,
                    entity.y - math.sin(0) * entity.size/2 + offset,
                    (255, 200, 100, 150),  # 橙黄色拖尾
                    -entity.speed * 0.2, 0, 10, 2, 0.9, 0
                )
    elif hasattr(entity, 'type') and entity.type == "坦克":
        # 坦克敌人使用六边形
        n_sides = 6
        radius = entity.size // 2
        points = []
        for i in range(n_sides):
            angle = 2 * math.pi * i / n_sides
            points.append((screen_x + radius * math.cos(angle), 
                          screen_y + radius * math.sin(angle)))
        pygame.draw.polygon(screen, entity.color, points)
        
        # 添加装甲纹理
        inner_radius = radius * 0.7
        inner_points = []
        for i in range(n_sides):
            angle = 2 * math.pi * i / n_sides
            inner_points.append((screen_x + inner_radius * math.cos(angle), 
                               screen_y + inner_radius * math.sin(angle)))
        pygame.draw.polygon(screen, (entity.color[0]-30, entity.color[1]-30, entity.color[2]-30), inner_points)
    elif hasattr(entity, 'type') and entity.type == "射手":
        # 射手敌人使用星形
        pygame.draw.rect(screen, entity.color, (screen_x - entity.size//2, screen_y - entity.size//2, entity.size, entity.size))
        # 添加炮管
        pygame.draw.rect(screen, (200, 200, 200), (screen_x, screen_y - entity.size//4, entity.size//2, entity.size//2))
    elif hasattr(entity, 'color') and isinstance(entity.color, tuple) and len(entity.color) >= 3 and entity.color[0] == 0 and entity.color[1] == 191 and entity.color[2] == 255:  # 队友
        # 使用三角形但添加更多细节
        points = [
            (screen_x, screen_y - entity.size//2),  # 顶点
            (screen_x - entity.size//2, screen_y + entity.size//2),  # 左下
            (screen_x + entity.size//2, screen_y + entity.size//2)   # 右下
        ]
        pygame.draw.polygon(screen, entity.color, points)
        
        # 添加内部细节
        inner_points = [
            (screen_x, screen_y - entity.size//4),  # 顶点
            (screen_x - entity.size//4, screen_y + entity.size//4),  # 左下
            (screen_x + entity.size//4, screen_y + entity.size//4)   # 右下
        ]
        # 安全地计算深色版本
        darker_color = (max(0, entity.color[0]-30), max(0, entity.color[1]-30), max(0, entity.color[2]-30))
        pygame.draw.polygon(screen, darker_color, inner_points)
    else:  # 玩家或普通敌人
        if isinstance(entity, Player) or (hasattr(entity, 'color') and entity.color == (0, 0, 255)):  # 玩家
            # 玩家使用圆角矩形
            entity_surface = pygame.Surface((entity.size, entity.size), pygame.SRCALPHA)
            pygame.draw.rect(entity_surface, (0, 0, 255), (0, 0, entity.size, entity.size), border_radius=5)
            
            # 添加高光效果
            highlight_rect = pygame.Rect(entity.size//4, entity.size//4, entity.size//2, entity.size//2)
            pygame.draw.rect(entity_surface, (100, 100, 255), highlight_rect, border_radius=3)
            
            screen.blit(entity_surface, (screen_x - entity.size//2, screen_y - entity.size//2))
        elif hasattr(entity, 'color'):  # 普通敌人
            pygame.draw.rect(screen, entity.color, (screen_x - entity.size//2, screen_y - entity.size//2, entity.size, entity.size))
        else:  # 没有颜色属性的实体
            pygame.draw.rect(screen, (255, 255, 255), (screen_x - entity.size//2, screen_y - entity.size//2, entity.size, entity.size))
    
    # 绘制生命值条（带有渐变色和边框）
    hp_width = 50
    hp_height = 5
    hp_x = screen_x - hp_width // 2
    hp_y = screen_y - entity.size//2 - 15
    
    # 血条边框
    pygame.draw.rect(screen, (40, 40, 40), (hp_x-1, hp_y-1, hp_width+2, hp_height+2))
    
    # 血条背景（半透明）
    bg_surface = pygame.Surface((hp_width, hp_height), pygame.SRCALPHA)
    pygame.draw.rect(bg_surface, (60, 60, 60, 180), (0, 0, hp_width, hp_height))
    screen.blit(bg_surface, (hp_x, hp_y))
    
    # 计算血量比例
    if hasattr(entity, 'max_health'):
        hp_ratio = entity.health / entity.max_health
    else:
        hp_ratio = entity.health / 100
    
    # 根据血量比例计算渐变色
    if hp_ratio > 0.6:  # 血量充足，绿色
        hp_color = (max(0, min(255, int(255 * (1 - hp_ratio)))), 255, 0)
    elif hp_ratio > 0.3:  # 血量中等，黄色
        hp_color = (255, max(0, min(255, int(255 * (hp_ratio - 0.3) / 0.3))), 0)
    else:  # 血量低，红色
        hp_color = (255, 0, 0)
    
    # 绘制血条填充
    if hp_ratio > 0:
        hp_fill_width = int(hp_width * hp_ratio)
        pygame.draw.rect(screen, hp_color, (hp_x, hp_y, hp_fill_width, hp_height))