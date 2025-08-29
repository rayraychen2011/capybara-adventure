######################載入套件######################
import pygame
import os
from enum import Enum


######################音樂類型列舉######################
class MusicType(Enum):
    """
    音樂類型列舉\n
    \n
    定義遊戲中不同場景的背景音樂類型\n
    """
    DEFAULT = "default"  # 預設背景音樂
    FOREST = "forest"    # 森林音樂
    TOWN = "town"        # 小鎮音樂
    LEGENDARY_TERRITORY = "legendary_territory"  # 傳奇動物領地音樂


######################音效類型列舉######################
class SoundEffectType(Enum):
    """
    音效類型列舉\n
    \n
    定義遊戲中的環境音效\n
    """
    GRASSLAND_WIND = "grassland_wind"  # 草原風聲


######################音樂管理系統######################
class MusicManager:
    """
    音樂管理系統 - 處理背景音樂切換和環境音效\n
    \n
    負責：\n
    1. 背景音樂的載入和播放\n
    2. 根據玩家位置/事件切換音樂\n
    3. 環境音效的管理\n
    4. 音量控制和淡入淡出效果\n
    """

    def __init__(self):
        """
        初始化音樂管理器\n
        """
        # 初始化 pygame mixer
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
                print("音樂系統初始化成功")
            except pygame.error as e:
                print(f"音樂系統初始化失敗: {e}")
                self.enabled = False
                return

        self.enabled = True
        self.current_music = None
        self.music_volume = 0.5  # 音樂音量 (0.0 - 1.0)
        self.sfx_volume = 0.7    # 音效音量 (0.0 - 1.0)
        
        # 音樂檔案路徑對應表
        self.music_files = {
            MusicType.DEFAULT: "assets/music/lost-in-dreams-abstract-chill-downtempo-cinematic-future-beats-270241.mp3",
            MusicType.FOREST: "assets/music/wrong-place-129242.mp3",
            MusicType.TOWN: "assets/music/town-street-1-350400.mp3",
            MusicType.LEGENDARY_TERRITORY: "assets/music/horror-background-atmosphere-156462.mp3"
        }
        
        # 音效檔案路徑對應表
        self.sound_files = {
            SoundEffectType.GRASSLAND_WIND: "assets/sounds/desert-wind-1-350398.wav"
        }
        
        # 載入的音效
        self.loaded_sounds = {}
        
        # 當前播放狀態
        self.is_music_playing = False
        self.current_sound_effects = set()  # 正在播放的音效
        
        # 載入音效檔案
        self._load_sound_effects()
        
        print("音樂管理器初始化完成")

    def _load_sound_effects(self):
        """
        載入所有音效檔案\n
        """
        for sound_type, file_path in self.sound_files.items():
            try:
                if os.path.exists(file_path):
                    sound = pygame.mixer.Sound(file_path)
                    sound.set_volume(self.sfx_volume)
                    self.loaded_sounds[sound_type] = sound
                    print(f"載入音效: {sound_type.value}")
                else:
                    print(f"音效檔案不存在: {file_path}")
                    # 創建空音效替代
                    self.loaded_sounds[sound_type] = self._create_mock_sound(sound_type.value)
            except pygame.error as e:
                print(f"載入音效失敗 {sound_type.value}: {e}")
                self.loaded_sounds[sound_type] = self._create_mock_sound(sound_type.value)

    def _create_mock_sound(self, sound_name):
        """
        創建模擬音效（當檔案不存在時）\n
        """
        try:
            # 創建一個很短的靜音
            mock_sound = pygame.mixer.Sound(buffer=b'\x00' * 1024)
            mock_sound.set_volume(0.1)
            print(f"創建模擬音效: {sound_name}")
            return mock_sound
        except:
            return None

    def play_music(self, music_type, loop=-1, fade_in_ms=1000):
        """
        播放背景音樂\n
        \n
        參數:\n
        music_type (MusicType): 音樂類型\n
        loop (int): 循環次數，-1 表示無限循環\n
        fade_in_ms (int): 淡入時間（毫秒）\n
        """
        if not self.enabled:
            return

        # 如果已經在播放相同音樂，不重複播放
        if self.current_music == music_type and self.is_music_playing:
            return

        file_path = self.music_files.get(music_type)
        if not file_path:
            print(f"未找到音樂類型: {music_type}")
            return

        try:
            # 停止當前音樂
            if self.is_music_playing:
                pygame.mixer.music.fadeout(500)  # 淡出500ms

            # 檢查檔案是否存在
            if os.path.exists(file_path):
                pygame.mixer.music.load(file_path)
                pygame.mixer.music.set_volume(self.music_volume)
                pygame.mixer.music.play(loop, fade_ms=fade_in_ms)
                
                self.current_music = music_type
                self.is_music_playing = True
                print(f"播放音樂: {music_type.value}")
            else:
                print(f"音樂檔案不存在: {file_path}")
                # 使用預設音樂替代
                if music_type != MusicType.DEFAULT:
                    self.play_music(MusicType.DEFAULT, loop, fade_in_ms)

        except pygame.error as e:
            print(f"播放音樂失敗 {music_type.value}: {e}")

    def stop_music(self, fade_out_ms=1000):
        """
        停止背景音樂\n
        \n
        參數:\n
        fade_out_ms (int): 淡出時間（毫秒）\n
        """
        if not self.enabled or not self.is_music_playing:
            return

        try:
            pygame.mixer.music.fadeout(fade_out_ms)
            self.is_music_playing = False
            self.current_music = None
            print("背景音樂已停止")
        except pygame.error as e:
            print(f"停止音樂失敗: {e}")

    def play_sound_effect(self, sound_type, loop=False):
        """
        播放音效\n
        \n
        參數:\n
        sound_type (SoundEffectType): 音效類型\n
        loop (bool): 是否循環播放\n
        """
        if not self.enabled:
            return

        sound = self.loaded_sounds.get(sound_type)
        if sound:
            try:
                loops = -1 if loop else 0
                sound.play(loops=loops)
                if loop:
                    self.current_sound_effects.add(sound_type)
                print(f"播放音效: {sound_type.value}")
            except pygame.error as e:
                print(f"播放音效失敗 {sound_type.value}: {e}")

    def stop_sound_effect(self, sound_type):
        """
        停止特定音效\n
        \n
        參數:\n
        sound_type (SoundEffectType): 要停止的音效類型\n
        """
        if not self.enabled:
            return

        sound = self.loaded_sounds.get(sound_type)
        if sound:
            try:
                sound.stop()
                self.current_sound_effects.discard(sound_type)
                print(f"停止音效: {sound_type.value}")
            except pygame.error as e:
                print(f"停止音效失敗 {sound_type.value}: {e}")

    def stop_all_sound_effects(self):
        """
        停止所有音效\n
        """
        if not self.enabled:
            return

        for sound_type in list(self.current_sound_effects):
            self.stop_sound_effect(sound_type)

    def set_music_volume(self, volume):
        """
        設定音樂音量\n
        \n
        參數:\n
        volume (float): 音量 (0.0 - 1.0)\n
        """
        self.music_volume = max(0.0, min(1.0, volume))
        if self.enabled and self.is_music_playing:
            pygame.mixer.music.set_volume(self.music_volume)

    def set_sfx_volume(self, volume):
        """
        設定音效音量\n
        \n
        參數:\n
        volume (float): 音量 (0.0 - 1.0)\n
        """
        self.sfx_volume = max(0.0, min(1.0, volume))
        for sound in self.loaded_sounds.values():
            if sound:
                sound.set_volume(self.sfx_volume)

    def update_music_for_location(self, terrain_type, in_legendary_territory=False):
        """
        根據位置更新背景音樂\n
        \n
        參數:\n
        terrain_type (int): 地形代碼\n
        in_legendary_territory (bool): 是否在傳奇動物領地\n
        """
        if not self.enabled:
            return

        # 優先級：傳奇動物領地 > 森林 > 小鎮 > 預設
        if in_legendary_territory:
            self.play_music(MusicType.LEGENDARY_TERRITORY)
        elif terrain_type == 1:  # 森林地形
            self.play_music(MusicType.FOREST)
        elif terrain_type == 5:  # 住宅區/小鎮
            self.play_music(MusicType.TOWN)
        else:
            self.play_music(MusicType.DEFAULT)

    def play_grassland_ambient(self, terrain_type):
        """
        播放草原環境音效\n
        \n
        參數:\n
        terrain_type (int): 地形代碼\n
        """
        if not self.enabled:
            return

        # 地形代碼 3 代表草原
        if terrain_type == 3:
            if SoundEffectType.GRASSLAND_WIND not in self.current_sound_effects:
                self.play_sound_effect(SoundEffectType.GRASSLAND_WIND, loop=True)
        else:
            # 離開草原時停止風聲
            if SoundEffectType.GRASSLAND_WIND in self.current_sound_effects:
                self.stop_sound_effect(SoundEffectType.GRASSLAND_WIND)

    def cleanup(self):
        """
        清理音樂管理器資源\n
        """
        if self.enabled:
            self.stop_music(fade_out_ms=500)
            self.stop_all_sound_effects()
            print("音樂管理器資源已清理")