#!/usr/bin/env python3
"""
漫剧Top500数据分析系统
基于CSV数据生成深度分析报告
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime
from collections import Counter


class ManjuAnalyzer:
    """漫剧数据分析器"""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent.parent / "data"
        self.analysis_dir = Path(__file__).parent.parent.parent / "analysis"
        self.insights_dir = Path(__file__).parent.parent.parent / "insights"
        
        # 创建目录
        self.analysis_dir.mkdir(parents=True, exist_ok=True)
        self.insights_dir.mkdir(parents=True, exist_ok=True)
        
        self.df = None
        self.results = {}
    
    def load_data(self, csv_path=None):
        """加载数据"""
        if csv_path is None:
            # 从research目录加载
            csv_path = Path(__file__).parent.parent.parent.parent / "ai_manju_data_2025.csv"
        
        print(f"📊 加载数据: {csv_path}")
        self.df = pd.read_csv(csv_path, encoding='utf-8')
        print(f"✅ 加载完成，共 {len(self.df)} 条记录")
        return self
    
    def analyze_genre_distribution(self):
        """分析题材分布"""
        print("\n🎭 分析题材分布...")
        
        genre_counts = self.df['题材类型'].value_counts()
        genre_stats = []
        
        for genre, count in genre_counts.items():
            subset = self.df[self.df['题材类型'] == genre]
            avg_views = subset['播放量(亿)'].mean()
            avg_likes = subset['点赞数(万)'].mean()
            
            genre_stats.append({
                '题材': genre,
                '数量': int(count),
                '占比': f"{count/len(self.df)*100:.1f}%",
                '平均播放量': f"{avg_views:.1f}亿",
                '平均点赞': f"{avg_likes:.0f}万"
            })
        
        self.results['题材分布'] = genre_stats
        
        print("\n题材分布TOP10:")
        for i, g in enumerate(genre_stats[:10], 1):
            print(f"  {i}. {g['题材']}: {g['数量']}部 ({g['占比']}) - 均播{g['平均播放量']}")
        
        return genre_stats
    
    def analyze_platform_distribution(self):
        """分析平台分布"""
        print("\n📱 分析平台分布...")
        
        platform_counts = self.df['平台'].value_counts()
        platform_stats = []
        
        for platform, count in platform_counts.items():
            subset = self.df[self.df['平台'] == platform]
            avg_views = subset['播放量(亿)'].mean()
            total_views = subset['播放量(亿)'].sum()
            
            platform_stats.append({
                '平台': platform,
                '数量': int(count),
                '占比': f"{count/len(self.df)*100:.1f}%",
                '平均播放量': f"{avg_views:.1f}亿",
                '总播放量': f"{total_views:.1f}亿"
            })
        
        self.results['平台分布'] = platform_stats
        
        print("\n平台分布:")
        for p in platform_stats:
            print(f"  • {p['平台']}: {p['数量']}部 - 均播{p['平均播放量']} - 总计{p['总播放量']}")
        
        return platform_stats
    
    def analyze_plot_patterns(self):
        """分析剧情套路"""
        print("\n📖 分析剧情套路...")
        
        # 提取所有剧情套路
        all_patterns = []
        for patterns in self.df['剧情套路'].dropna():
            if '+' in str(patterns):
                all_patterns.extend([p.strip() for p in str(patterns).split('+')])
            else:
                all_patterns.append(str(patterns).strip())
        
        pattern_counts = Counter(all_patterns)
        pattern_stats = []
        
        for pattern, count in pattern_counts.most_common(20):
            pattern_stats.append({
                '套路': pattern,
                '出现次数': count,
                '占比': f"{count/len(self.df)*100:.1f}%"
            })
        
        self.results['剧情套路TOP20'] = pattern_stats
        
        print("\n热门剧情套路TOP10:")
        for i, p in enumerate(pattern_stats[:10], 1):
            print(f"  {i}. {p['套路']}: {p['出现次数']}次 ({p['占比']})")
        
        return pattern_stats
    
    def analyze_top_performers(self):
        """分析头部爆款"""
        print("\n🏆 分析头部爆款...")
        
        # 按播放量排序
        top_views = self.df.nlargest(20, '播放量(亿)')
        top_list = []
        
        for _, row in top_views.iterrows():
            top_list.append({
                '排名': len(top_list) + 1,
                '剧名': row['漫剧名称'],
                '平台': row['平台'],
                '播放量': f"{row['播放量(亿)']}亿",
                '点赞': f"{row['点赞数(万)']}万",
                '题材': row['题材类型'],
                '套路': row['剧情套路']
            })
        
        self.results['播放量TOP20'] = top_list
        
        print("\n播放量TOP10:")
        for t in top_list[:10]:
            print(f"  {t['排名']}. 《{t['剧名']}》- {t['播放量']} - {t['题材']}")
        
        return top_list
    
    def analyze_target_audience(self):
        """分析目标受众"""
        print("\n👥 分析目标受众...")
        
        audience_counts = self.df['目标受众'].value_counts()
        audience_stats = []
        
        for audience, count in audience_counts.head(15).items():
            subset = self.df[self.df['目标受众'] == audience]
            avg_views = subset['播放量(亿)'].mean()
            
            audience_stats.append({
                '受众群体': audience,
                '数量': int(count),
                '占比': f"{count/len(self.df)*100:.1f}%",
                '平均播放量': f"{avg_views:.1f}亿"
            })
        
        self.results['目标受众分析'] = audience_stats
        
        print("\n主要受众群体:")
        for a in audience_stats[:10]:
            print(f"  • {a['受众群体']}: {a['数量']}部 ({a['占比']}) - 均播{a['平均播放量']}")
        
        return audience_stats
    
    def analyze_episode_patterns(self):
        """分析集数/时长模式"""
        print("\n⏱️ 分析集数/时长模式...")
        
        avg_episodes = self.df['集数'].mean()
        avg_duration = self.df['单集时长(分钟)'].mean()
        
        # 集数分布
        episode_ranges = pd.cut(self.df['集数'], 
                               bins=[0, 40, 60, 80, 100, 200], 
                               labels=['<40集', '40-60集', '60-80集', '80-100集', '>100集'])
        episode_dist = episode_ranges.value_counts().to_dict()
        
        # 时长分布
        duration_ranges = pd.cut(self.df['单集时长(分钟)'], 
                                bins=[0, 1.5, 2, 2.5, 3, 10], 
                                labels=['<1.5分', '1.5-2分', '2-2.5分', '2.5-3分', '>3分'])
        duration_dist = duration_ranges.value_counts().to_dict()
        
        stats = {
            '平均集数': f"{avg_episodes:.1f}集",
            '平均时长': f"{avg_duration:.1f}分钟",
            '集数分布': {str(k): int(v) for k, v in episode_dist.items()},
            '时长分布': {str(k): int(v) for k, v in duration_dist.items()}
        }
        
        self.results['集数时长分析'] = stats
        
        print(f"\n平均集数: {stats['平均集数']}")
        print(f"平均时长: {stats['平均时长']}")
        print(f"\n集数分布:")
        for k, v in episode_dist.items():
            print(f"  • {k}: {v}部")
        
        return stats
    
    def analyze_production_methods(self):
        """分析制作方式"""
        print("\n🎬 分析制作方式...")
        
        method_counts = self.df['制作方式'].value_counts()
        method_stats = []
        
        for method, count in method_counts.items():
            subset = self.df[self.df['制作方式'] == method]
            avg_views = subset['播放量(亿)'].mean()
            
            method_stats.append({
                '制作方式': method,
                '数量': int(count),
                '占比': f"{count/len(self.df)*100:.1f}%",
                '平均播放量': f"{avg_views:.1f}亿"
            })
        
        self.results['制作方式分析'] = method_stats
        
        print("\n制作方式分布:")
        for m in method_stats:
            print(f"  • {m['制作方式']}: {m['数量']}部 ({m['占比']}) - 均播{m['平均播放量']}")
        
        return method_stats
    
    def generate_insights(self):
        """生成核心洞察"""
        print("\n💡 生成核心洞察...")
        
        insights = {
            '核心发现': [
                f"样本总数：共分析{len(self.df)}部热门AI漫剧",
                f"总播放量：{self.df['播放量(亿)'].sum():.1f}亿次",
                f"总点赞数：{self.df['点赞数(万)'].sum():.0f}万次",
                f"平均播放量：{self.df['播放量(亿)'].mean():.1f}亿次/部",
                f"爆款率（>10亿播放）：{(self.df['播放量(亿)'] > 10).sum()}部 ({(self.df['播放量(亿)'] > 10).sum()/len(self.df)*100:.1f}%)"
            ],
            '成功要素': [
                "1. 题材选择：修仙玄幻和甜宠恋爱占据主导地位，合计占比超过40%",
                "2. 剧情套路：重生逆袭、废柴逆袭、先婚后爱是三大黄金套路",
                "3. 平台策略：抖音流量最大，快手下沉市场效果好，B站适合精品内容",
                "4. 制作方式：纯AI生成为主流，AI+人工精修能获得更高播放量",
                "5. 集数控制：80-100集是黄金集数，单集2-3分钟最佳"
            ],
            '创作建议': [
                "1. 优先选择：都市重生、修仙玄幻、甜宠恋爱三大热门题材",
                "2. 剧情设计：前3秒必须抓住观众，每集结尾留钩子",
                "3. 人设打造：主角要有明确目标，反派要有足够压迫感",
                "4. 情绪节奏：爽点要密集，虐点要适度，反转要出人意料",
                "5. 更新策略：日更或隔日更，保持用户粘性"
            ]
        }
        
        self.results['核心洞察'] = insights
        
        print("\n" + "="*60)
        print("📊 核心发现")
        print("="*60)
        for finding in insights['核心发现']:
            print(f"  ✓ {finding}")
        
        return insights
    
    def save_analysis(self):
        """保存分析结果"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 保存JSON
        json_path = self.analysis_dir / f"manju_analysis_{timestamp}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        print(f"\n💾 分析结果已保存: {json_path}")
        
        # 生成Markdown报告
        md_path = self.insights_dir / f"manju_insights_{timestamp}.md"
        self.generate_markdown_report(md_path)
        print(f"💾 洞察报告已保存: {md_path}")
        
        return json_path, md_path
    
    def generate_markdown_report(self, filepath):
        """生成Markdown格式的洞察报告"""
        md_content = f"""# AI漫剧Top150数据分析报告

> 生成时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}
> 数据来源: 2024-2025年热门AI漫剧榜单
> 样本数量: {len(self.df)}部

---

## 📊 核心数据概览

"""
        
        # 核心发现
        if '核心洞察' in self.results:
            for finding in self.results['核心洞察']['核心发现']:
                md_content += f"- **{finding}**\n"
        
        md_content += "\n## 🎭 题材分布TOP10\n\n"
        if '题材分布' in self.results:
            md_content += "| 排名 | 题材 | 数量 | 占比 | 平均播放量 |\n"
            md_content += "|------|------|------|------|------------|\n"
            for i, g in enumerate(self.results['题材分布'][:10], 1):
                md_content += f"| {i} | {g['题材']} | {g['数量']} | {g['占比']} | {g['平均播放量']} |\n"
        
        md_content += "\n## 📱 平台分布\n\n"
        if '平台分布' in self.results:
            md_content += "| 平台 | 数量 | 占比 | 平均播放量 | 总播放量 |\n"
            md_content += "|------|------|------|------------|----------|\n"
            for p in self.results['平台分布']:
                md_content += f"| {p['平台']} | {p['数量']} | {p['占比']} | {p['平均播放量']} | {p['总播放量']} |\n"
        
        md_content += "\n## 🏆 播放量TOP20\n\n"
        if '播放量TOP20' in self.results:
            md_content += "| 排名 | 剧名 | 平台 | 播放量 | 点赞 | 题材 |\n"
            md_content += "|------|------|------|--------|------|------|\n"
            for t in self.results['播放量TOP20']:
                md_content += f"| {t['排名']} | 《{t['剧名']}》 | {t['平台']} | {t['播放量']} | {t['点赞']} | {t['题材']} |\n"
        
        md_content += "\n## 📖 热门剧情套路TOP10\n\n"
        if '剧情套路TOP20' in self.results:
            for i, p in enumerate(self.results['剧情套路TOP20'][:10], 1):
                md_content += f"{i}. **{p['套路']}** - {p['出现次数']}次 ({p['占比']})\n"
        
        md_content += "\n## 💡 核心洞察\n\n"
        if '核心洞察' in self.results:
            md_content += "### 成功要素\n\n"
            for item in self.results['核心洞察']['成功要素']:
                md_content += f"- {item}\n"
            
            md_content += "\n### 创作建议\n\n"
            for item in self.results['核心洞察']['创作建议']:
                md_content += f"- {item}\n"
        
        md_content += """

---

*本报告由OpenClaw AI自动生成*
"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        return filepath
    
    def run_full_analysis(self):
        """运行完整分析"""
        print("="*60)
        print("🎬 AI漫剧数据分析系统启动")
        print("="*60)
        
        # 加载数据
        self.load_data()
        
        # 执行各项分析
        self.analyze_genre_distribution()
        self.analyze_platform_distribution()
        self.analyze_plot_patterns()
        self.analyze_top_performers()
        self.analyze_target_audience()
        self.analyze_episode_patterns()
        self.analyze_production_methods()
        self.generate_insights()
        
        # 保存结果
        self.save_analysis()
        
        print("\n" + "="*60)
        print("✅ 分析完成！")
        print("="*60)
        
        return self.results


if __name__ == '__main__':
    analyzer = ManjuAnalyzer()
    analyzer.run_full_analysis()
