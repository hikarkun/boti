#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PiggyCell 自动游戏机器人
支持自动玩游戏、获取Kode permainan、记录分数
"""

import json
import os
import sys
import time
import logging
import requests
import schedule
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import random
import colorlog
from fake_useragent import UserAgent
import warnings
import urllib3

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

class PiggyGameBot:
    def __init__(self, config_path: str = "config/config.json"):
        """初始化游戏机器人"""
        self.config_path = config_path
        self.config = self.load_config()
        self.accounts = self.load_accounts()
        self.proxies = self.load_proxies()
        self.user_agent = UserAgent()
        self.setup_logging()
        
    def load_config(self) -> Dict:
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.error(f"配置文件不存在: {self.config_path}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            self.logger.error(f"配置文件格式错误: {e}")
            sys.exit(1)
    
    def load_accounts(self) -> List[Dict[str, str]]:
        """加载Akun信息"""
        json_accounts_path = "config/accounts.json"
        
        try:
            with open(json_accounts_path, 'r', encoding='utf-8') as f:
                accounts_data = json.load(f)
                accounts = []
                for account in accounts_data.get('accounts', []):
                    if account.get('enabled', True):
                        accounts.append({
                            'name': account['name'],
                            'session_token': account['session_token'],
                            'cookies': account.get('cookies', ''),
                            'description': account.get('description', '')
                        })
                return accounts
        except FileNotFoundError:
            print("错误: Akun配置文件不存在，请创建config/accounts.json文件")
            return []
        except (json.JSONDecodeError, KeyError) as e:
            print(f"警告: JSONAkun配置文件格式错误: {e}")
            return []
    
    def load_proxies(self) -> List[str]:
        """加载代理信息"""
        proxies = []
        try:
            with open("proxy.txt", 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        proxies.append(line)
        except FileNotFoundError:
            print("警告: proxy.txt文件不存在")
        
        return proxies
    
    def setup_logging(self):
        """设置日志"""
        log_level = getattr(logging, self.config.get('log_level', 'INFO'))
        
        # 创建logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)
        
        # 清除现有的handlers
        self.logger.handlers.clear()
        
        # 文件处理器（无颜色）
        file_handler = logging.FileHandler('piggy_game_bot.log', encoding='utf-8')
        file_handler.setLevel(log_level)
        file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        
        # 控制台处理器（带颜色）
        console_handler = colorlog.StreamHandler()
        console_handler.setLevel(log_level)
        console_formatter = colorlog.ColoredFormatter(
            '%(log_color)s%(asctime)s - %(levelname)s - %(message)s%(reset)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
        )
        console_handler.setFormatter(console_formatter)
        
        # 添加handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def get_random_proxy(self) -> Optional[Dict[str, str]]:
        """获取随机代理"""
        if not self.proxies:
            return None
        
        proxy_url = random.choice(self.proxies)
        return {
            'http': proxy_url,
            'https': proxy_url
        }
    
    def get_random_user_agent(self) -> str:
        """获取随机User-Agent"""
        try:
            return self.user_agent.random
        except Exception:
            user_agents = [
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:115.0) Gecko/20100101 Firefox/115.0',
                'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.86 Safari/537.36',
                'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
                'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.110 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/119.0.2151.44 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0',
                'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.76 YaBrowser/24.1.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 12_6_3; rv:115.0) Gecko/20100101 Firefox/115.0',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_7_10) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6170.45 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6; rv:110.0) Gecko/20100101 Firefox/110.0',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.129 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.169 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.43 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3; rv:102.0) Gecko/20100101 Firefox/102.0'
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
                'Mozilla/5.0 (iPhone; CPU iPhone OS 16_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.2 Mobile/15E148 Safari/604.1',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 12_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15',
                'Mozilla/5.0 (iPad; CPU OS 15_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Mobile/15E148 Safari/604.1',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_5_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1 Safari/605.1.15',
                'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.7 Mobile/15E148 Safari/604.1',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1 Safari/605.1.15',
                'Mozilla/5.0 (iPad; CPU OS 14_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.5 Mobile/15E148 Safari/604.1',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1 Safari/605.1.15',
                'Mozilla/5.0 (iPhone; CPU iPhone OS 13_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.6 Mobile/15E148 Safari/604.1',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0 Safari/605.1.15',
                'Mozilla/5.0 (iPad; CPU OS 13_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.3 Mobile/15E148 Safari/604.1',
                'Mozilla/5.0 (iPhone; CPU iPhone OS 12_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.4 Mobile/15E148 Safari/604.1',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15',
                'Mozilla/5.0 (iPad; CPU OS 16_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Mobile/15E148 Safari/604.1',
                'Mozilla/5.0 (iPhone; CPU iPhone OS 15_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Mobile/15E148 Safari/604.1',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 12_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6 Safari/605.1.15',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15',
                'Mozilla/5.0 (iPhone; CPU iPhone OS 11_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.4 Mobile/15E148 Safari/604.1',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0 Safari/605.1.15',
                'Mozilla/5.0 (iPad; CPU OS 12_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.5 Mobile/15E148 Safari/604.1',
                'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_3 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) Version/10.0 Mobile/14G60 Safari/602.1',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/601.7.8 (KHTML, like Gecko) Version/11.1 Safari/601.7.8',
                'Mozilla/5.0 (iPad; CPU OS 11_4 like Mac OS X) AppleWebKit/604.5.6 (KHTML, like Gecko) Version/11.4 Mobile/15E148 Safari/604.1',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/600.8.9 (KHTML, like Gecko) Version/10.1 Safari/600.8.9',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.85.17 (KHTML, like Gecko) Version/9.1 Safari/537.85.17',
                'Mozilla/5.0 (iPhone; CPU iPhone OS 9_3_5 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.3 Mobile/13G36 Safari/601.1',
                'Mozilla/5.0 (iPad; CPU OS 10_3_3 like Mac OS X) AppleWebKit/603.3.8 (KHTML, like Gecko) Version/10.3 Mobile/14G60 Safari/603.3.8',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/536.30.1 (KHTML, like Gecko) Version/8.0 Safari/536.30.1',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/534.57.2 (KHTML, like Gecko) Version/7.1 Safari/534.57.2'
            ]
            return random.choice(user_agents)
    
    def get_game_id(self, account: Dict[str, str]) -> Optional[str]:
        """生成游戏ID"""
        try:
            # 生成一个随机的游戏ID
            import uuid
            import time
            
            # 生成基于时间戳和随机数的游戏ID
            timestamp = int(time.time() * 1000)  # 毫秒时间戳
            random_part = str(uuid.uuid4()).replace('-', '')[:8]  # 8位随机字符串
            game_id = f"{timestamp}_{random_part}"
            
            self.logger.info(f"Akun {account['name']} 生成游戏ID: {game_id}")
            return game_id
                
        except Exception as e:
            self.logger.error(f"Akun {account['name']} 生成游戏ID失败: {e}")
            return None
    
    def get_game_code(self, account: Dict[str, str]) -> Optional[str]:
        """获取Kode permainan"""
        try:
            # 生成游戏ID作为Kode permainan
            game_id = self.get_game_id(account)
            if not game_id:
                self.logger.warning(f"Akun {account['name']} 无法生成游戏ID")
                return None
            
            # 直接使用生成的游戏ID作为Kode permainan
            self.logger.info(f"Akun {account['name']} 使用生成的游戏ID作为Kode permainan: {game_id}")
            return game_id
                
        except Exception as e:
            self.logger.error(f"Akun {account['name']} 获取Kode permainan失败: {e}")
            return None
    
    def check_game_code(self, account: Dict[str, str], game_code: str) -> bool:
        """检查Kode permainan"""
        try:
            headers = {
                'accept': '*/*',
                'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,ja;q=0.6,fr;q=0.5,ru;q=0.4,und;q=0.3',
                'content-type': 'application/json',
                'origin': 'https://app.piggycell.io',
                'referer': 'https://app.piggycell.io/en/game/piggy-game?mode=regular',
                'user-agent': self.get_random_user_agent(),
                'sec-ch-ua': '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"macOS"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'trpc-accept': 'application/jsonl',
                'x-trpc-source': 'nextjs-react'
            }
            
            cookies = f"__Secure-authjs.session-token={account['session_token']}"
            if account['cookies']:
                cookies += f"; {account['cookies']}"
            headers['cookie'] = cookies
            
            data = {"0": {"json": {"gameCode": game_code}}}
            
            proxy = self.get_random_proxy()
            session = requests.Session()
            session.verify = False
            
            response = session.post(
                "https://app.piggycell.io/api/trpc/piggyGame.checkGameCode?batch=1",
                headers=headers,
                json=data,
                proxies=proxy,
                timeout=30
            )
            
            if response.status_code == 200:
                self.logger.info(f"Akun {account['name']} Kode permainan {game_code} 验证成功")
                return True
            else:
                self.logger.error(f"Akun {account['name']} Kode permainanVerifikasi gagal，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Akun {account['name']} Kode permainanVerifikasi gagal: {e}")
            return False
    
    def record_game_score(self, account: Dict[str, str], score: int) -> bool:
        """记录游戏分数"""
        try:
            headers = {
                'accept': '*/*',
                'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,ja;q=0.6,fr;q=0.5,ru;q=0.4,und;q=0.3',
                'content-type': 'application/json',
                'origin': 'https://app.piggycell.io',
                'referer': 'https://app.piggycell.io/en/game/piggy-game?mode=regular',
                'user-agent': self.get_random_user_agent(),
                'sec-ch-ua': '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"macOS"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'trpc-accept': 'application/jsonl',
                'x-trpc-source': 'nextjs-react'
            }
            
            cookies = f"__Secure-authjs.session-token={account['session_token']}"
            if account['cookies']:
                cookies += f"; {account['cookies']}"
            headers['cookie'] = cookies
            
            data = {"0": {"json": {"score": score}}}
            
            proxy = self.get_random_proxy()
            session = requests.Session()
            session.verify = False
            
            response = session.post(
                "https://app.piggycell.io/api/trpc/piggyGame.recordGameScore?batch=1",
                headers=headers,
                json=data,
                proxies=proxy,
                timeout=30
            )
            
            if response.status_code == 200:
                self.logger.info(f"Akun {account['name']} 记录分数 {score} 成功")
                return True
            else:
                self.logger.error(f"Akun {account['name']} 记录分数失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Akun {account['name']} 记录分数失败: {e}")
            return False
    
    def play_single_game(self, account: Dict[str, str], game_round: int) -> bool:
        """执行单次游戏"""
        try:
            account_desc = f" ({account.get('description', '')})" if account.get('description') else ""
            self.logger.info(f"Akun {account['name']}{account_desc} 开始第{game_round}次游戏")
            
            # 1. 获取Kode permainan
            game_code = self.get_game_code(account)
            if not game_code:
                self.logger.error(f"Akun {account['name']} 第{game_round}次游戏获取代码失败")
                return False
            
            # 如果Kode permainan为None，说明没有游戏次数，跳过
            if game_code is None:
                return False
            
            # 2. 验证Kode permainan
            if not self.check_game_code(account, game_code):
                self.logger.error(f"Akun {account['name']} 第{game_round}次Kode permainanVerifikasi gagal")
                return False
            
            # 3. 模拟游戏过程（这里可以添加实际的游戏逻辑）
            # 使用配置文件中的分数范围
            min_score = self.config.get('game_settings', {}).get('min_score', 65)
            max_score = self.config.get('game_settings', {}).get('max_score', 100)
            score = random.randint(min_score, max_score)
            self.logger.info(f"Akun {account['name']} 第{game_round}次游戏完成，得分: {score}")
            
            # 4. 记录分数
            if self.record_game_score(account, score):
                self.logger.info(f"Akun {account['name']} 第{game_round}次游戏完成")
                return True
            else:
                self.logger.error(f"Akun {account['name']} 第{game_round}次游戏记录分数失败")
                return False
                
        except Exception as e:
            self.logger.error(f"Akun {account['name']} 第{game_round}次游戏失败: {e}")
            return False
    
    def play_game(self, account: Dict[str, str]) -> bool:
        """执行多次游戏"""
        try:
            account_desc = f" ({account.get('description', '')})" if account.get('description') else ""
            games_count = self.config.get('game_settings', {}).get('games_per_session', 3)
            self.logger.info(f"Akun {account['name']}{account_desc} 开始执行{games_count}次游戏")
            
            success_count = 0
            for i in range(1, games_count + 1):
                result = self.play_single_game(account, i)
                if result is False:  # 如果返回False，说明没有游戏次数，跳出循环
                    self.logger.info(f"Akun {account['name']} 没有游戏次数，停止游戏")
                    break
                elif result:  # 如果返回True，说明游戏成功
                    success_count += 1
                
                # 游戏间延迟
                if i < games_count:  # 最后一次不需要延迟
                    delay = self.config.get('game_settings', {}).get('game_delay', 1)
                    self.logger.info(f"Akun {account['name']} 等待{delay}秒后进行下一次游戏...")
                    time.sleep(delay)
            
            self.logger.info(f"Akun {account['name']} 完成{games_count}次游戏，成功: {success_count}/{games_count}")
            return success_count > 0  # 只要有一次成功就认为成功
            
        except Exception as e:
            self.logger.error(f"Akun {account['name']} 游戏失败: {e}")
            return False
    
    def play_all_accounts(self):
        """为所有Akun执行游戏"""
        if not self.accounts:
            self.logger.warning("没有找到Akun信息")
            return
        
        self.logger.info(f"开始为 {len(self.accounts)} 个Akun执行游戏")
        
        success_count = 0
        for account in self.accounts:
            if self.play_game(account):
                success_count += 1
            
            # Akun间延迟
            time.sleep(random.uniform(1, 3))
        
        self.logger.info(f"游戏完成，成功: {success_count}/{len(self.accounts)}")
    
    def run_scheduler(self):
        """Run scheduled tasks"""
        self.logger.info("Program started, executing gameplay immediately...")
        self.play_all_accounts()

        interval = self.config.get('game_settings', {}).get('session_interval', 5)
        schedule.every(interval).seconds.do(self.play_all_accounts)

        self.logger.info(f"Scheduled gameplay: every {interval} seconds")
        self.logger.info("Press Ctrl+C to stop the program")

        try:
            while True:
                schedule.run_pending()
                time.sleep(3)  # check every second
        except KeyboardInterrupt:
            self.logger.info("Program stopped")

    
    def run_once(self):
        """立即执行一次游戏"""
        self.play_all_accounts()

def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] == '--once':
        # 立即执行一次游戏
        bot = PiggyGameBot()
        bot.run_once()
    else:
        # 运行定时任务
        bot = PiggyGameBot()
        bot.run_scheduler()

if __name__ == "__main__":
    main()
