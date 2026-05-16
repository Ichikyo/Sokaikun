import discord
from discord.ext import commands
from discord import app_commands
from discord import Interaction
from typing import Optional
import datetime
import random
import re
import os
from keep_alive import keep_alive
import asyncio
from collections import defaultdict
from dataclasses import dataclass


# ==========================================
# 設定・定数
# ==========================================
ROLE_PARTICIPANT = "参加者"
ROLE_DELEGATED = "委任者"
ROLE_DELEGATOR = "委任宣言者"
ROLE_VENUE_STAFF = "会議場係"
ROLE_HANGOUT_STAFF = "ふくおんせい係"
VC_SOKAI_NAME = "総会"
SOKAIKUN_ID = 1386751629923057827  # SokaikunのユーザーID


# ==========================================
# データ構造の定義（ゲームのセーブデータ用）
# ==========================================
@dataclass
class GameData:
    step: int = 0              # 進行状況 (0:初期, 10:処理中, etc)
    clear: int = 0             # クリア状態 (0:未クリア, 1:ステージ3到達, 2:完全クリア)
    hi_score: int = 0          # ハイスコア
    sokaikun_coin: int = 65535 # Sokaikunの手持ちコイン
    player_coin: int = 0       # プレイヤーの手持ちコイン
    table_coin: int = 0        # テーブル上のコイン
    borrow_coin: int = 0       # 借りたコインの数


# グローバルセーブデータ（ユーザーIDをキーにしてGameDataを保存）
savedata = defaultdict(GameData)


# ==========================================
# Botの初期化
# ==========================================
class SokaikunBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!", 
            intents=discord.Intents.all()
        )

    async def setup_hook(self):
        # 起動時にスラッシュコマンドを同期
        await self.tree.sync()
        # 再起動しても生成済みのボタンに反応できるようになる
        for i in discord.ui.View.__subclasses__():
            try:
                if i.__name__.startswith("death"):
                    self.add_view(i("test_id"))
                else:
                    self.add_view(i())
                print(f"Registered: {i.__name__}")
            except Exception as e:
                print(f"Failed {i.__name__}: {e}")
        # アクティビティ変更ループをバックグラウンドで開始
        self.loop.create_task(self.change_activity_loop())
        print("Sokaikunが起動しました。")

    async def change_activity_loop(self):
        await self.wait_until_ready()
        activities = [
            "🍣", "♟️", "💿", "🥜", "🎴", "🀄", "🃏", "👻", "🐑", "🦕", "🎲", 
            "🛕", "🎆", "🪺", "🏝️", "💎", "🐢", "🪐", "🐘", "🐺", "⚗️", "🧑‍🌾", 
            "🦙", "💀", "🕵️", "💣", "👨‍🦲", "🫅", "🐧", "💍", "🤖", "🚂", "🍀", 
            "🥯", "🍰", "🧰", "🛣️", "🥒", "🌌", "🕷️", "🎪", "⚡", "🏔️", "🌳", 
            "🏪", "🏰", "🏀", "🧙‍♂️", "🎣", "🐵", "🔪", "🍛", "🤞", "🪬", "💰", 
            "👑", "👁️", "🔍", "☣️", "🚫", "󠁧󠁢󠁳󠁣🏴󠁧󠁢󠁳󠁣󠁴󠁿", "󠁧󠁢󠁷󠁬🎞️"
        ]
        while not self.is_closed():
            activity = random.choice(activities)
            await self.change_presence(activity=discord.Game(activity))
            await asyncio.sleep(10000)


bot = SokaikunBot()


# ==========================================
# テキスト生成ヘルパー関数
# ==========================================
async def venue_comment():
    comment_list = [
        "スレッドを作成したよ！", "会議場へようこそ！", "テキチャ勢も参加ありがとう！",
        "良いアイデアの気配……！", "今日はどんな議題が挙がったのかな？", "本総会のメインチャットはこちら！",
        "# っ🫖 🍵🍵🍵", '*"未来とは、今である。"*\n-# マーガレット・ミード'
    ]
    weight_list = [15, 15, 15, 15, 15, 15, 5, 5]
    return random.choices(comment_list, weights=weight_list)[0]


async def hangout_comment():
    zodiac_list = ['おひつじ座','おうし座','ふたご座','かに座','しし座','おとめ座','てんびん座','さそり座','いて座','やぎ座','みずがめ座','うお座']
    boardgame_list = ['パッチワーク','花火','スシゴー','こねこばくはつ','AZUL','宝石の煌き','それはオレの牧場だ！','スーパーメガラッキーボックス','ニムト','ドブル','SKULL','JUST ONE',"キング・オブ・トーキョー","ウィザード","ウボンゴ"]
    trpg_list = ['CoC','シノビガミ','ソード・ワールド','フィアスコ','怪談白物語','サタスペ','ダブルクロス','ゆうやけこやけ','パラノイア','アリアンロッド']
    comment_list = [
        "ハロー、ここは総会ふくおんせいスレッド。", "アイデアをどんどん膨らませよう！",
        f"今日の1位は……\n## {random.choice(['おめでとう！','すご～い！','やったね♪'])}✨{random.choice(zodiac_list)}のキミ✨\nラッキーボドゲは「{random.choice(boardgame_list)}」だよ！",
        f"今日の12位は……\n## {random.choice(['残念！','ごめんなさ～い、','あらら。。。'])}💥{random.choice(zodiac_list)}のキミ💥\nでも大丈夫！ラッキーTRPGの「{random.choice(trpg_list)}」をやってハッピーに過ごそう！",
        "Hello, Hangout-Thread!", "# っ🫖 🍵🍵🍵", "一方そのころ、ロシアでは……",
        "ドーモ。チェス研民=サン。Sokaikunです。", f"しりとり、……{random.choice(['りんご！','量子コンピュータ！','リヴァイアサン！'])}",
        "{いい感じに盛り上がるコメントを入力}", "*雑談。つまり、くだらない話だから価値がある。有益な話なら、本屋で本を買えばいい。*\n-# 星 新一",
        f"@here\n# 激レア！今日はハッピーデイ🍀"
    ]
    weight_list = [12, 12, 30, 10, 5, 5, 5, 5, 5, 5, 5, 1]
    return random.choices(comment_list, weights=weight_list)[0]


# ==========================================
# UIコンポーネント (View())
# ==========================================
class DelegationView(discord.ui.View):
    # 委任ボタンのViewクラス
    def __init__(self):
        # タイムアウトなしでずっとボタンを押せるようにする
        super().__init__(timeout=None)

    @discord.ui.button(label="委任", style=discord.ButtonStyle.primary, custom_id="del_on_id")
    async def del_on(self, interaction: discord.Interaction, button: discord.ui.Button):
        member = interaction.guild.get_member(interaction.user.id)
        del_role = discord.utils.get(interaction.guild.roles, name=ROLE_DELEGATOR)
        
        if not del_role:
            return await interaction.response.send_message(f"エラー: ロール[{ROLE_DELEGATOR}]を見つけられませんでした。", ephemeral=True)
            
        if discord.utils.get(member.roles, id=del_role.id):
            await interaction.response.send_message(f"ロール[{ROLE_DELEGATOR}]は既に付与されています。", ephemeral=True)
        else:
            try:
                await member.add_roles(del_role)
                await interaction.response.send_message(f"ロールを付与しました: {del_role.name}", ephemeral=True)
            except discord.Forbidden:
                await interaction.response.send_message("エラー: ロールを付与できません。権限が不足しています。", ephemeral=True)

    @discord.ui.button(label="取消", style=discord.ButtonStyle.danger, custom_id="del_off_id")
    async def del_off(self, interaction: discord.Interaction, button: discord.ui.Button):
        member = interaction.guild.get_member(interaction.user.id)
        del_role = discord.utils.get(interaction.guild.roles, name=ROLE_DELEGATOR)
        
        if not del_role:
            return await interaction.response.send_message(f"エラー: ロール[{ROLE_DELEGATOR}]を見つけられませんでした。", ephemeral=True)

        if discord.utils.get(member.roles, id=del_role.id):
            try:
                await member.remove_roles(del_role)
                await interaction.response.send_message(f"ロールを削除しました: {del_role.name}", ephemeral=True)
            except discord.Forbidden:
                await interaction.response.send_message("エラー: ロールを削除できません。権限が不足しています。", ephemeral=True)
        else:
            await interaction.response.send_message("委任は既に解除されています。", ephemeral=True)


# ==========================================
# 一般・便利コマンド
# ==========================================
@bot.tree.command(name="hello", description="Say hello to the world!") 
async def hello(interaction: discord.Interaction): 
    await interaction.response.send_message("Hello, World!")


@bot.tree.command(name="info_sokaikun", description="Sokaikunについて説明します。")
async def info_sokaikun(interaction: discord.Interaction):
    info_text = (
        "# チェス研総会管理bot [Sokaikun]について\n"
        "## はじめに\n"
        "Sokaikunはichikiyoが作成したチェス研究会用のDiscordBotです。"
        "GitHubにアップロードしたソースコードをRender, UptimeRobot, GoogleAppsScriptによって常時起動しているため、"
        "それらのサイトやDiscord自体の変更によって機能停止する場合があることをご了承ください。\n"
        "サーバーでのコマンド実行が主な機能ですが、一部のコマンドはSokaikunへのDMでも実行可能です。\n"
        "## セットアップ\n"
        "Sokaikunに管理者権限を与えてサーバーに招待したら、それぞれロール名が 参加者 , 委任者 , 委任宣言者 , 会議場係 , ふくおんせい係 である5つのロールを作成し、"
        "Sokaikunのロールをそれらより上位に設定してください。"
        "また、総会を行うボイスチャンネルの名前は 総会 としておいてください。\n"
        "## コマンド\n"
        "- **/hello** [DMでも実行可能]\n"
        "Hello, World!と返します。テスト用コマンドです。"
        "原因不明のエラーが出た時など、Sokaikunが動作しているかを確かめるためにも使えます。\n"
        "- **/info_sokaikun** [DMでも実行可能]\n"
        "このメッセージを返します。\n"
        "- **/dice** [DMでも実行可能]\n"
        "引数にダイスコマンドを入れるとダイスを振ります。"
        "◯d◯+◯d◯+◯など、ダイスコマンドや数値同士の加算も可能です。"
        "減算は実装されていませんが、1d3+-1のようにマイナスの数値を足すことはできます。\n"
        "- **/game** [DMでも実行可能]\n"
        "Sokaikunとのゲームを始めるボタンを生成します。付属コマンドとして**/coin**, **/reset**, **/shop**があります。\n"
        "-# クリアできた人は教えて！\n"
        "- **/del** [管理者のみ実行可能]\n"
        "委任の宣言・解除を行うボタンを作成します。"
        "[委任宣言者]という名前のロールに対応するボタンが作成されます。"
        "次回総会を委任予定の人はボタン[委任]を押してください。委任票は参加者へランダムに振り分けられます。"
        "但し、特定の人物に票を委任したい場合はボタンを押さずに一般チャンネルへ書き込んでください。\n"
        "- **/sokai_1** [管理者のみ実行可能]\n"
        "ボイスチャンネル 総会 に接続しているメンバーを取得し、参加者一覧として表示します。"
        "参加者の中で委任宣言者ロールが付与されているメンバーがいた場合、その委任宣言者ロールを削除します。"
        "その後、その時点での委任宣言者ロールの保有者数を委任票として、参加者へランダムに振り分けます。"
        "獲得した委任票の数は参加者一覧の名前横に (+◯) の形で表示され、その数が余分に獲得した投票数となります。"
        "獲得した委任票が0票の場合は名前横に何も表示されません。"
        "このコマンドを実行後、 [参加者ロール保有者] = [ボイスチャンネル#総会に接続していたメンバー] となります。\n"
        "- **/sokai_2** [管理者のみ実行可能]\n"
        "委任宣言者ロール保有者を取得し、委任者一覧として表示します。"
        "このコマンドを実行後、 [委任者ロール保有者] = [元委任宣言者ロール保有者] , [委任宣言者ロール保有者] = [なし] となります。\n"
        "**/sokai_1**および**/sokai_2**は、特定の人物への名指し委任があった場合を想定して分離されています。"
        "**/sokai_1**を実行後、名指し委任を行った委任者に手動で委任宣言者ロールを付与し、**/sokai_2**を実行してください。"
        "名指し委任は**/sokai_1**で計上できないため、各自で確認する必要があります。\n"
        "- **/sokai_3** [管理者のみ実行可能]\n"
        "Sokaikun自身にロール[会議場係], [ふくおんせい係]が付与されているかを確認し、付与されているロールに応じてスレッド[会議場], [ふくおんせい]を作成します。"
        "どちらのロールも付与されていない場合は無効なコマンドです。\n"
        "- **/sokai_all** [管理者のみ実行可能]\n"
        "**/sokai_1**, **/sokai_2**, **/sokai_3**をつなげて使用できるコマンドです。"
        "名指しの委任が無かった場合、すなわち全員が**/del**のボタンで委任を宣言した場合にはこのコマンドを使用してください。\n"
        "## おわりに\n"
        "「なんか変だな」と思った挙動はバグかもしれませんのでどうぞichikiyoまでお知らせください。\n"
        "Sokaikunのソースコードはこちら→GitHub: <https://github.com/Ichikyo/Sokaikun>"
    )
    await interaction.response.send_message(info_text)


@bot.tree.command(name="dice", description="ダイスを振ります。")
async def dice(interaction: discord.Interaction, ダイス: str):
    if interaction.user.bot: return
    content = ダイス.replace(' ', '')
    splitPlus = content.split('+')
    response = content.replace('+', ' + ') + ": "
    result = 0
    
    for (i, context) in enumerate(splitPlus):
        splited = context.split('d')
        if len(splited) == 1:
            result += int(splited[0])
            response += splited[0]
        else:
            num_dice = int(splited[0])
            dice_faces = int(splited[1])
            for dice in range(num_dice):
                res = random.randint(1, dice_faces)
                result += res
                response += str(res)
                if num_dice > 1 and dice != num_dice - 1:
                    response += " + "
                elif dice == num_dice - 1 and len(splitPlus) == 1:
                    response += " = " + str(result)
        
        if len(splitPlus) > 1:
            if i != len(splitPlus) - 1:
                response += " + "
            else:
                response += " = " + str(result)

    await interaction.response.send_message(response)


# ==========================================
# 総会管理コマンド
# ==========================================
@bot.tree.command(name="del", description="委任宣言開始 要管理者権限")
@app_commands.guild_only()
@app_commands.default_permissions(administrator=True)
async def delpanel(interaction: discord.Interaction):
    await interaction.response.send_message(embed=discord.Embed(description="委任を開始しました！", color=discord.Color.green()))

    del_embed = discord.Embed(
        title="総会の委任はこちらから", 
        description="特定の人物に委任したい場合は、ボタンを押さずに一般チャンネルへその旨を記載してください", 
        color=discord.Color.green()
    )
    await interaction.channel.send(embed=del_embed, view=DelegationView())


@bot.tree.command(name="sokai_1", description="総会Step1 参加者更新&委任票集計 要管理者権限")
@discord.app_commands.guild_only()
@discord.app_commands.default_permissions(administrator=True)
async def sokai_1(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)
    now_date = (datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=9)).date()

    sokai_vc = discord.utils.get(interaction.guild.voice_channels, name=VC_SOKAI_NAME)

    if not sokai_vc or not sokai_vc.members:
        # このエラーメッセージは「考え中」の表示形式を引き継ぐため、ephemeral=Trueにできない。
        return await interaction.followup.send(f"エラー: ボイスチャンネル[{VC_SOKAI_NAME}]に誰もいません。")

    del_role = discord.utils.get(interaction.guild.roles, name=ROLE_DELEGATOR)
    par_role = discord.utils.get(interaction.guild.roles, name=ROLE_PARTICIPANT)

    if not del_role or not par_role:
        return await interaction.followup.send("エラー: 必要なロールが見つかりません。")

    # 既存の参加者ロールをクリア
    for i in par_role.members:
          try:
              await i.remove_roles(par_role)
          except discord.Forbidden:
              await interaction.followup.send("エラー: ロールを削除できません。権限が不足している可能性があります。")
              return

    par_member = sokai_vc.members
    par_member_name = sorted([i.display_name for i in par_member])
    del_number = [0] * len(par_member)
    par_and_del_set = set(par_member) & set(del_role.members) # &はandではいけない

    # 参加者から委任宣言者ロールを削除
    for i in par_and_del_set:
        try:
            await i.remove_roles(del_role)
        except discord.Forbidden:
            await interaction.followup.send("エラー: ロールを削除できません。権限が不足している可能性があります。")
            return

    # 正しい委任宣言者のメンバーを取得
    correct_del_role = discord.utils.get(interaction.guild.roles, name=ROLE_DELEGATOR)

    # 委任票のランダム振り分け
    if correct_del_role.members:
        del_number_index = random.choices(range(len(par_member)), k=len(correct_del_role.members))
        for i in del_number_index:
            del_number[i] += 1

    # メッセージ構築（参加者）
    sokai_1_message = f"{now_date}　総会\n### 参加者\n"
    sokai_1_message += "、".join([par_member_name[i] + f"(+{str(del_number[i])})" for i in range(len(par_member))])

    # ロール付与
    for i in par_member:
        try:
            await i.add_roles(par_role)
        except discord.Forbidden:
            await interaction.followup.send("エラー: ロールを付与できません。権限が不足している可能性があります。")
            return

    # メッセージ送信
    await interaction.followup.send(sokai_1_message.replace("(+0)", ""))


@bot.tree.command(name="sokai_2", description="総会Step2 委任者更新 要管理者権限")
@discord.app_commands.guild_only()
@discord.app_commands.default_permissions(administrator=True)
async def sokai_2(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)

    sokai_vc = discord.utils.get(interaction.guild.voice_channels, name=VC_SOKAI_NAME)

    if not sokai_vc or not sokai_vc.members:
        return await interaction.followup.send(f"エラー: ボイスチャンネル[{VC_SOKAI_NAME}]に誰もいません。")

    deled_role = discord.utils.get(interaction.guild.roles, name=ROLE_DELEGATED)
    del_role = discord.utils.get(interaction.guild.roles, name=ROLE_DELEGATOR)

    if not deled_role or not del_role:
        return await interaction.followup.send("エラー: 必要なロールが見つかりません。")

    # 既存の委任者ロールをクリア
    for i in deled_role.members:
        try:
            await i.remove_roles(deled_role)
        except discord.Forbidden:
            await interaction.followup.send("エラー: ロールを削除できません。権限が不足している可能性があります。")
            return

    # ロール移行
    for i in del_role.members:
        try:
            await i.add_roles(deled_role)
            await i.remove_roles(del_role)
        except discord.Forbidden:
            await interaction.followup.send("エラー: ロールを付与または削除できません。権限が不足している可能性があります。")
            return

    # メッセージ構築（委任者）
    sokai_2_message = "### 委任者\n"
    new_deled_role = discord.utils.get(interaction.guild.roles, name=ROLE_DELEGATED)
    if new_deled_role:
        sokai_2_message += "、".join(sorted([i.display_name for i in new_deled_role.members]))

    # メッセージ送信
    await interaction.followup.send(sokai_2_message)


@bot.tree.command(name="sokai_3", description="総会Step3 総会用スレッド作成 要管理者権限")
@discord.app_commands.guild_only()
@discord.app_commands.default_permissions(administrator=True)
async def sokai_3(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)
    now_date = (datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=9)).date()

    # スレッド作成
    sokaikun = interaction.guild.get_member(SOKAIKUN_ID)
    venue_role = discord.utils.get(interaction.guild.roles, name = ROLE_VENUE_STAFF)
    hangout_role = discord.utils.get(interaction.guild.roles, name = ROLE_HANGOUT_STAFF)

    if (venue_role and venue_role in sokaikun.roles) or (hangout_role and hangout_role in sokaikun.roles):
        sokai_3_message = "テキストチャット用スレッドはこちら\n"
        if venue_role in sokaikun.roles:
            venue_thread = await interaction.channel.create_thread(name=f"{now_date} 会議場", type=discord.ChannelType.public_thread)
            await venue_thread.send(await venue_comment())
            sokai_3_message += f"{venue_thread.jump_url}　"
        if hangout_role in sokaikun.roles:
            hangout_thread = await interaction.channel.create_thread(name=f"{now_date} ふくおんせい", type=discord.ChannelType.public_thread)
            await hangout_thread.send(await hangout_comment())
            sokai_3_message += hangout_thread.jump_url
    else:
        await interaction.followup.send(f"ボクはロール[{ROLE_VENUE_STAFF}], [{ROLE_HANGOUT_STAFF}]のどちらも持ってないよ！")
        return

    # メッセージ送信
    await interaction.followup.send(sokai_3_message)


@bot.tree.command(name="sokai_all", description="総会Step1～3 要管理者権限")
@app_commands.guild_only()
@app_commands.default_permissions(administrator=True)
async def sokai_all(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)
    now_date = (datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=9)).date()

    sokai_vc = discord.utils.get(interaction.guild.voice_channels, name=VC_SOKAI_NAME)
    if not sokai_vc or not sokai_vc.members:
        return await interaction.followup.send(f"エラー: ボイスチャンネル[{VC_SOKAI_NAME}]に誰もいません。")
        
    par_role = discord.utils.get(interaction.guild.roles, name=ROLE_PARTICIPANT)
    deled_role = discord.utils.get(interaction.guild.roles, name=ROLE_DELEGATED)
    del_role = discord.utils.get(interaction.guild.roles, name=ROLE_DELEGATOR)

    if not del_role or not par_role or not deled_role:
        return await interaction.followup.send("エラー: 必要なロールが見つかりません。")

    # 既存の参加者・委任者ロールをクリア
    for i in par_role.members:
        try:
            await i.remove_roles(par_role)
        except discord.Forbidden:
            await interaction.followup.send("エラー: ロールを削除できません。権限が不足している可能性があります。")
            return
    for i in deled_role.members:
        try:
            await i.remove_roles(deled_role)
        except discord.Forbidden:
            await interaction.followup.send("エラー: ロールを削除できません。権限が不足している可能性があります。")
            return

    par_member = sokai_vc.members
    par_member_name = sorted([i.display_name for i in par_member])
    del_number = [0] * len(par_member)
    par_and_del_set = set(par_member) & set(del_role.members) # &はandではいけない

    # 参加者から委任宣言者ロールを削除
    for i in par_and_del_set:
        try:
            await i.remove_roles(del_role)
        except discord.Forbidden:
            await interaction.followup.send("エラー: ロールを削除できません。権限が不足している可能性があります。")
            return

    # 正しい委任宣言者のメンバーを取得
    correct_del_role = discord.utils.get(interaction.guild.roles, name=ROLE_DELEGATOR)

    # 委任票のランダム振り分け
    if correct_del_role.members:
        del_number_index = random.choices(range(len(par_member)), k=len(correct_del_role.members))
        for i in del_number_index:
            del_number[i] += 1

    # メッセージ構築（参加者）
    sokai_all_message = f"{now_date}　総会\n### 参加者\n"
    sokai_all_message += "、".join([f"{par_member_name[i]}(+{del_number[i]})" for i in range(len(par_member))])

    # ロール付与・移行
    for i in par_member:
        try:
            await i.add_roles(par_role)
        except discord.Forbidden:
            await interaction.followup.send("エラー: ロールを付与できません。権限が不足している可能性があります。")
            return
    for i in correct_del_role.members:
        try:
            await i.add_roles(deled_role)
            await i.remove_roles(correct_del_role)
        except discord.Forbidden:
            await interaction.followup.send("エラー: ロールを付与または削除できません。権限が不足している可能性があります。")
            return

    # メッセージ構築（委任者）
    sokai_all_message += "\n### 委任者\n"
    new_deled_role = discord.utils.get(interaction.guild.roles, name=ROLE_DELEGATED)
    if new_deled_role:
        sokai_all_message += "、".join(sorted([i.display_name for i in new_deled_role.members]))

    # スレッド作成
    sokaikun = interaction.guild.get_member(SOKAIKUN_ID)
    venue_role = discord.utils.get(interaction.guild.roles, name=ROLE_VENUE_STAFF)
    hangout_role = discord.utils.get(interaction.guild.roles, name=ROLE_HANGOUT_STAFF)

    if (venue_role and venue_role in sokaikun.roles) or (hangout_role and hangout_role in sokaikun.roles):
        sokai_all_message += "\n\nテキストチャット用スレッドはこちら\n"
        if venue_role in sokaikun.roles:
            thread = await interaction.channel.create_thread(name=f"{now_date} 会議場", type=discord.ChannelType.public_thread)
            await thread.send(await venue_comment())
            sokai_all_message += f"{thread.jump_url}　"
        if hangout_role in sokaikun.roles:
            thread = await interaction.channel.create_thread(name=f"{now_date} ふくおんせい", type=discord.ChannelType.public_thread)
            await thread.send(await hangout_comment())
            sokai_all_message += thread.jump_url

    # メッセージ送信
    await interaction.followup.send(sokai_all_message.replace("(+0)", ""))


# ==========================================
# ミニゲーム用UIコンポーネント (Modal, View)
# ==========================================
class GameBorrowModal(discord.ui.Modal, title='ステージ1'):
    # ゲーム開始時の借り入れコイン入力モーダル
    borrow_input = discord.ui.TextInput(
        label='何枚借りる？',
        placeholder='コインを借りる枚数を入力(数字のみ)',
        required=True,
        max_length=5
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            borrowed_coin = int(self.borrow_input.value)
        except ValueError:
            return await interaction.response.send_message("「0から65533までの数字だけを入力してね。」", ephemeral=True)

        if 0 <= borrowed_coin <= 65533:
            data = savedata[interaction.user.id]
            data.step = 10
            data.player_coin = borrowed_coin + 1
            data.borrow_coin = borrowed_coin
            data.sokaikun_coin = 65533 - borrowed_coin

            death_ask_borrow_embed = discord.Embed(title=f"借りる枚数は、{data.borrow_coin}枚でいい？", color=discord.Color.blue())
            data.step = 3
            await interaction.response.send_message(embed=death_ask_borrow_embed, view=death_3_View(user_id=interaction.user.id))
        else:
            await interaction.response.send_message("「0から65533までの数字だけを入力してね。」", ephemeral=True)


class yattare_View(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="はい", style=discord.ButtonStyle.primary, custom_id="yattare_id")
    async def yattare(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = interaction.user.id
        data = savedata[user_id]

        if data.step == 0:
            data.step = 10
            data.sokaikun_coin = 65534
            data.player_coin = 1
            data.step = 1
            await interaction.response.send_message("「オーケー！」", ephemeral=True)
            try:
                thread = await interaction.channel.create_thread(name=f"{interaction.user.name}とのゲーム", type=discord.ChannelType.private_thread)
                await thread.add_user(interaction.user)
            except:
                thread = interaction.channel
            await thread.send("「ようこそ！ここがキミとのゲームスペースさ！」")
            await asyncio.sleep(3)
            await thread.send(f"「そしてこれが…ゲームにつかう{interaction.user.name}コイン！」")
            await thread.send(file=discord.File(R"illust/kiminocoin.png"))
            await asyncio.sleep(3)
            await thread.send("「当然キミとのゲームに使うためだけに製造したものだよ！」")
            await asyncio.sleep(3)
            await thread.send("「全部で65535枚あるからじゃんじゃん使えるね！」")
            await thread.send(file=discord.File(R"illust/yamamori.png"))
            await asyncio.sleep(3)
            await thread.send("「ゲームの参加賞として、はい！1枚あげる！」")
            await asyncio.sleep(3)
            await thread.send("「/coinで今のコイン所持状況が分かるよ。やってみて！」")
            await asyncio.sleep(3)
            await thread.send("「準備ができたらルール説明を始めるね！」")
            await asyncio.sleep(3)
            death_yattare_embed = discord.Embed(title="準備はできた？", color=discord.Color.blue())

            await thread.send(embed=death_yattare_embed, view=death_1_View(user_id=interaction.user.id))
        else:
            await interaction.response.send_message("もう始まってるよ！やり直したい場合はスレッド内で/resetを使ってね。", ephemeral=True)


class death_reset_View(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=None)
        self.death_reset.custom_id = f"death_reset_{user_id}"

    @discord.ui.button(label="/reset", style=discord.ButtonStyle.danger)
    async def death_reset(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = interaction.user.id
        data = savedata[user_id]
        if button.custom_id.endswith(f"{user_id}"):
            if data.step == 0:
                await interaction.response.send_message("「/gameで始められるゲームで使うボタンだよ！」", ephemeral=True)
            else:
                await death_stage1_rule(interaction)
        else:
            await interaction.response.send_message("「これはキミ用のボタンじゃないよ。」", ephemeral=True)


class ResetButtonMixin:
    # どのViewに混ぜても「/reset」ボタンを追加できるクラス。
    # discord.ui.View を継承しないことで、多重継承時の初期化トラブルを防ぎます。

    @discord.ui.button(label="/reset", style=discord.ButtonStyle.danger)
    async def death_reset(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = interaction.user.id
        data = savedata[user_id]

        if button.custom_id.endswith(f"{user_id}"):
            if data.step == 0:
                await interaction.response.send_message("「/gameで始められるゲームで使うボタンだよ！」", ephemeral=True)
            else:
                await death_stage1_rule(interaction)
        else:
            await interaction.response.send_message("「これはキミ用のボタンじゃないよ。」", ephemeral=True)


class death_1_View(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=None)
        self.death_1.custom_id = f"death_1_{user_id}"

    @discord.ui.button(label="はい", style=discord.ButtonStyle.primary)
    async def death_1(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await death_check(interaction):
            user_id = interaction.user.id
            data = savedata[user_id]
            data.step = 10

            await interaction.response.send_message("「オーケー！それじゃ、ゲームのルールを説明するね。」")
            await asyncio.sleep(3)
            await interaction.channel.send(f"「このゲームは全部で3つのステージから成り立っているよ！」")
            await asyncio.sleep(3)
            await interaction.channel.send("「ステージ1はステージ2の準備みたいなもので、勝っても負けてもいい。」")
            await asyncio.sleep(3)
            await interaction.channel.send("「ステージ2に勝つことができたらステージ3に進めるよ！」")
            await asyncio.sleep(3)
            await interaction.channel.send("「そして、キミの最終目的はステージ3をクリアすることだ！」")
            await asyncio.sleep(3)
            await interaction.channel.send("「各ステージのルールは以下にまとめておくね。」")
            await asyncio.sleep(3)
            rule_stage1_embed = discord.Embed(title="ステージ1: コラッツレイズ",
                description="ボクは65534枚のコインを持っている。"
                "ボクが手持ちコインのうち1枚をテーブルの上に置き、キミは残りの65533枚以下でボクからコインを借りてゲームを開始する。"
                "借りられなかった残り分はボクの手持ちコインとなる。"
                "ボクを先手とし、テーブルのコインに対して交互に①②③のどれかを行う。"
                "ただし、テーブルのコインを0枚にするような操作はできない。\n\n"
                "①レイズ: テーブルにあるコインとピッタリ同じ数のコインを手持ちのコインからテーブルに追加する\n"
                "②カット: テーブルにあるコインから1枚を取り、さらに残ったコインのピッタリ3分の2を取る\n"
                "③レイズ&ギブ: テーブルにあるコインとピッタリ同じ数のコインを手持ちのコインからテーブルに追加し、"
                "さらにその後テーブルにあるコインとピッタリ同じ数のコインを手持ちのコインから相手にあげる\n\n"
                "①②③のどれかを可能な限り行い、先にどれも行えなくなった方が負け。勝敗決定はルールによるもののみで、降参はなし。\n\n",
                color=discord.Color.green())
            await interaction.channel.send(embed=rule_stage1_embed)
            await asyncio.sleep(3)
            rule_stage2_embed = discord.Embed(title="ステージ2: カウントダウンゲーム",
                description="ステージ1の終了時点でテーブルに置かれていたコインをそのまま使用する。"
                "ゲーム1の勝者を先手としてテーブルの上から交互に1〜3枚ずつコインを取り、最後の1枚を相手に取らせたら勝ち。",
                color=discord.Color.green())
            await interaction.channel.send(embed=rule_stage2_embed)
            await asyncio.sleep(3)
            if data.clear >= 1:
                rule_stage3_embed = discord.Embed(title="ステージ3: ???",
                    description="ステージ2に勝ったら挑戦できる。"
                    "ステージ1で借りたコインの枚数だけ、キミの手持ちコインからボクにコインを返せればクリア。",
                    color=discord.Color.green())
                await interaction.channel.send(embed=rule_stage3_embed)
            else:
                rule_stage3_embed = discord.Embed(title="ステージ3: ???",
                    description="ステージ2に勝ったら挑戦できる。"
                    "ルールおよびクリア条件はまだ明かされない。",
                    color=discord.Color.green())
                await interaction.channel.send(embed=rule_stage3_embed)
                await asyncio.sleep(3)
                await interaction.channel.send("「ステージ3のルールは、キミが一度でもステージ2でボクに勝ったら教えてあげるよ。」")
                await asyncio.sleep(3)
                await interaction.channel.send("「まあ、説明するまでもないようなことなんだけどね。」")
            await asyncio.sleep(3)
            await interaction.channel.send("「ちなみに、/resetで今のこの状況に戻ってくることができるよ。」")
            await asyncio.sleep(3)
            await interaction.channel.send("「騒がしくしないように、このスレッド内で使ってね。」")
            await asyncio.sleep(3)
            await interaction.channel.send("「それじゃあテーブルに1枚だけコインを置くよ。/coinで確認できるからね！」")
            data.sokaikun_coin = 65533
            data.table_coin = 1
            await interaction.channel.send(file=discord.File(R"illust/hajimeruka.png"))
            await asyncio.sleep(3)
            await interaction.channel.send("「さっそく、ステージ1を始めよっか？」")
            await asyncio.sleep(3)
            death_1_embed = discord.Embed(title="何枚借りる？", color=discord.Color.blue())
            data.step = 2
            await interaction.channel.send(embed=death_1_embed, view=death_2_View(user_id=interaction.user.id))


class death_2_View(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=None)
        self.death_2.custom_id = f"death_2_{user_id}"

    @discord.ui.button(label="入力する", style=discord.ButtonStyle.primary)
    async def death_2(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await death_check(interaction):
            user_id = interaction.user.id
            data = savedata[user_id]
            await interaction.response.send_modal(GameBorrowModal())


class death_3_View(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=None)
        self.death_3_go.custom_id = f"death_3_go_{user_id}"
        self.death_3_re.custom_id = f"death_3_re_{user_id}"

    @discord.ui.button(label="はい", style=discord.ButtonStyle.primary)
    async def death_3_go(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await death_check(interaction):
            user_id = interaction.user.id
            data = savedata[user_id]
            await interaction.response.defer(thinking=True)
            await death_stage1_sokaikun(interaction)

    @discord.ui.button(label="訂正する", style=discord.ButtonStyle.danger)
    async def death_3_re(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await death_check(interaction):
            user_id = interaction.user.id
            data = savedata[user_id]
            await interaction.response.send_modal(GameBorrowModal())


class death_4_View(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=None)
        self.death_4_raise.custom_id = f"death_4_raise_{user_id}"
        self.death_4_cut.custom_id = f"death_4_cut_{user_id}"
        self.death_4_raiseandgive.custom_id = f"death_4_raiseandgive_{user_id}"

    @discord.ui.button(label="レイズ", style=discord.ButtonStyle.primary)
    async def death_4_raise(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await death_check(interaction):
            user_id = interaction.user.id
            data = savedata[user_id]
            data.step = 10

            await interaction.response.defer(thinking=True)
            await death_stage1_player(interaction, "raise")

    @discord.ui.button(label="カット", style=discord.ButtonStyle.primary)
    async def death_4_cut(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await death_check(interaction):
            user_id = interaction.user.id
            data = savedata[user_id]
            data.step = 10

            await interaction.response.defer(thinking=True)
            await death_stage1_player(interaction, "cut")

    @discord.ui.button(label="レイズ&ギブ", style=discord.ButtonStyle.primary)
    async def death_4_raiseandgive(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await death_check(interaction):
            user_id = interaction.user.id
            data = savedata[user_id]
            data.step = 10

            await interaction.response.defer(thinking=True)
            await death_stage1_player(interaction, "raiseandgive")


class death_5_View(discord.ui.View, ResetButtonMixin):
    def __init__(self, user_id):
        super().__init__(timeout=None)
        self.death_5.custom_id = f"death_5_{user_id}"
        self.death_reset.custom_id = f"death_reset_{user_id}"

    @discord.ui.button(label="はい", style=discord.ButtonStyle.primary)
    async def death_5(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await death_check(interaction):
            user_id = interaction.user.id
            data = savedata[user_id]
            data.step = 10

            await interaction.response.defer(thinking=True)
            await death_stage2_sokaikun(interaction)


class death_6_View(discord.ui.View, ResetButtonMixin):
    def __init__(self, user_id):
        super().__init__(timeout=None)
        self.death_6.custom_id = f"death_6_{user_id}"
        self.death_reset.custom_id = f"death_reset_{user_id}"

    @discord.ui.button(label="はい", style=discord.ButtonStyle.primary)
    async def death_6(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await death_check(interaction):
            user_id = interaction.user.id
            data = savedata[user_id]
            data.step = 10

            await interaction.response.send_message("「オーケー！まずはキミの番だね！」")
            death_6_embed = discord.Embed(title=f"テーブルのコイン: {data.table_coin}枚", color=discord.Color.blue())
            data.step = 7
            await interaction.channel.send(embed=death_6_embed, view=death_7_BaseView(user_id=interaction.user.id))


class death_7_BaseView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=None)
        self.death_7_one.custom_id = f"death_7_one_{user_id}"
        self.death_7_two.custom_id = f"death_7_two_{user_id}"
        self.death_7_three.custom_id = f"death_7_three_{user_id}"

    @discord.ui.button(label="1枚とる", style=discord.ButtonStyle.primary)
    async def death_7_one(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await death_check(interaction):
            user_id = interaction.user.id
            data = savedata[user_id]
            data.step = 10

            await interaction.response.defer(thinking=True)
            await death_stage2_player(interaction, 1)

    @discord.ui.button(label="2枚とる", style=discord.ButtonStyle.primary)
    async def death_7_two(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await death_check(interaction):
            user_id = interaction.user.id
            data = savedata[user_id]
            data.step = 10

            await interaction.response.defer(thinking=True)
            await death_stage2_player(interaction, 2)

    @discord.ui.button(label="3枚とる", style=discord.ButtonStyle.primary)
    async def death_7_three(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await death_check(interaction):
            user_id = interaction.user.id
            data = savedata[user_id]
            data.step = 10

            await interaction.response.defer(thinking=True)
            await death_stage2_player(interaction, 3)


class death_7_GoodView(death_7_BaseView):
    def __init__(self, user_id):
        super().__init__(user_id)
        self.death_7_result.custom_id = f"death_7_result_{user_id}"

    @discord.ui.button(label="結果まで飛ばす", style=discord.ButtonStyle.success)
    async def death_7_result(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await death_check(interaction):
            user_id = interaction.user.id
            data = savedata[user_id]
            data.step = 10

            await interaction.response.send_message("「オーケー！それじゃ、結果まで飛ばすよ。」")
            data.sokaikun_coin += data.table_coin // 4 * 3 + 1
            data.player_coin += (data.table_coin+2) // 4
            data.table_coin = 0
            await death_stage2_result(interaction)


class death_7_BadView(death_7_BaseView):
    def __init__(self, user_id):
        super().__init__(user_id)
        self.death_7_giveup.custom_id = f"death_7_giveup_{user_id}"

    @discord.ui.button(label="降参する", style=discord.ButtonStyle.danger)
    async def death_7_giveup(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await death_check(interaction):
            user_id = interaction.user.id
            data = savedata[user_id]
            data.step = 10

            await interaction.response.send_message("「オーケー！それじゃ、適当に結果まで進めるね。」")
            data.sokaikun_coin += data.table_coin // 4
            data.player_coin += data.table_coin*3 // 4 + 1
            data.table_coin = 0
            await death_stage2_giveup(interaction)


class death_8_View(discord.ui.View, ResetButtonMixin):
    def __init__(self, user_id):
        super().__init__(timeout=None)
        self.death_8.custom_id = f"death_8_{user_id}"
        self.death_reset.custom_id = f"death_reset_{user_id}"

    @discord.ui.button(label="はい", style=discord.ButtonStyle.primary)
    async def death_8(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await death_check(interaction):
            user_id = interaction.user.id
            data = savedata[user_id]
            data.step = 10

            await interaction.response.defer(thinking=True)
            if data.player_coin >= data.borrow_coin:
                data.sokaikun_coin += data.borrow_coin
                data.player_coin -= data.borrow_coin
                await interaction.followup.send(f"「うんうん、ピッタリ{data.borrow_coin}枚。確かに返してもらったよ！」")
                data.borrow_coin = 0
                await asyncio.sleep(3)
                await interaction.channel.send("「キミと遊べて楽しかったよ！付き合ってくれてありがとう！」")
                if data.clear == 1:
                    data.clear = 2
                    await interaction.channel.send(file=discord.File(R"illust/arigatou.png"))
                    await asyncio.sleep(3)
                    await interaction.channel.send("# ゲームクリアです。\n今後ともSokaikunをよろしくお願いします。")
                    await asyncio.sleep(3)
                    await interaction.channel.send("「……。」")
                    await asyncio.sleep(3)
                    await interaction.channel.send("「このゲーム、実はハイスコアチャレンジがあるんだ。」")
                    await asyncio.sleep(3)
                    await interaction.channel.send("「クリア後限定で解放される、/shopコマンドを使ったチャレンジだよ。」")
                    await asyncio.sleep(3)
                    await interaction.channel.send("「ルールの詳細もそこで確認できるから、良ければ/shopを実行してみてね。」")
            else:
                await interaction.followup.send("「手持ちコインの数が足りないみたいだね！」")
                await asyncio.sleep(0.3)
                await interaction.channel.send("「キヒヒッ！これじゃステージ3はクリアできないかな？」")
                await asyncio.sleep(0.3)
                await interaction.channel.send("「まだやる気があるなら、/resetで最初からやり直す？」")
                death_8_embed = discord.Embed(title="やり直す？", color=discord.Color.red())
                await interaction.channel.send(embed=death_8_embed, view=death_reset_View(user_id=interaction.user.id))
            data.step = 9


class death_shop_View(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=None)
        self.death_item_1.custom_id = f"death_item_1_{user_id}"
        self.death_item_2.custom_id = f"death_item_2_{user_id}"
        self.death_item_3.custom_id = f"death_item_3_{user_id}"

    @discord.ui.button(label="①を買う", style=discord.ButtonStyle.primary)
    async def death_item_1(self, interaction: discord.Interaction, button: discord.ui.Button):
        custom_id = interaction.data["custom_id"]
        user_id = interaction.user.id
        data = savedata[user_id]

        if custom_id.endswith(f"{interaction.user.id}"):
            if data.clear == 2:
                await interaction.response.send_message("「まいどあり！それじゃあこれをどうぞ！」")
                item_1_embed = discord.Embed(title="ハイスコアチャレンジのルール", description=
                    "/shopで購入できるアイテムを利用して、なるべく多くのコイン獲得を目指すゲーム。"
                    "借りたコインが0枚の状態で/coinを使用した際の、キミの手持ちコインが記録になる。/coinを使用しないと記録が更新されないので注意。\n"
                    "このチャレンジでは/shopで呼び出せるsokaiyaでアイテムを買うことができ、アイテムの購入にはその時点でのキミの手持ちコインを消費する。"
                    "アイテムの購入は任意のタイミングででき、借りたコインの枚数が0枚である必要もない。\n"
                    "アイテムの購入により消費したコインはゲームから除外され、ゲームに使われるコインの総枚数が代金分だけ減少する。"
                    "/resetによりアイテムの購入・使用状況はリセットされ、コインの総枚数も65535枚に戻る。", color=discord.Color.green())
                await interaction.channel.send(embed=item_1_embed)
            else:
                await interaction.response.send_message("「今はその段階じゃないよ。」", ephemeral=True)
        else:
            await interaction.response.send_message("「これはキミ用のボタンじゃないよ。」", ephemeral=True)

    @discord.ui.button(label="②を買う", style=discord.ButtonStyle.primary)
    async def death_item_2(self, interaction: discord.Interaction, button: discord.ui.Button):
        custom_id = interaction.data["custom_id"]
        user_id = interaction.user.id
        data = savedata[user_id]

        if custom_id.endswith(f"{interaction.user.id}"):
            if data.clear == 2:
                await interaction.response.send_message("「まいどあり！それじゃあこれをどうぞ！」")
                item_2_embed = discord.Embed(title="Sokaikunアルゴリズム解説書", description="ステージ1でSokaikunに行動選択の余地がある場合、以下のアルゴリズムで行動する。", color=discord.Color.green())
                item_2_embed.add_field(name="1. [レイズ]するパターン", value="下記の「[カット]するパターン」「[レイズ&ギブ]するパターン」のどちらにも当てはまらない場合", inline=False)
                item_2_embed.add_field(name="2. [カット]するパターン", value="パターン①: テーブルのコインが10枚の場合\n"
                    "パターン②: テーブルのコインが16枚、かつSokaikunの手持ちコインが21839枚以下の場合", inline=False)
                item_2_embed.add_field(name="3. [レイズ&ギブ]するパターン", value="テーブルのコインが2枚、かつSokaikunの手持ちコインが7枚以上の場合", inline=False)
                await interaction.channel.send(embed=item_2_embed)
            else:
                await interaction.response.send_message("「今はその段階じゃないよ。」", ephemeral=True)
        else:
            await interaction.response.send_message("「これはキミ用のボタンじゃないよ。」", ephemeral=True)

    @discord.ui.button(label="③を買う", style=discord.ButtonStyle.primary)
    async def death_item_3(self, interaction: discord.Interaction, button: discord.ui.Button):
        custom_id = interaction.data["custom_id"]
        user_id = interaction.user.id
        data = savedata[user_id]
        now_step = data.step
        data.step = 10

        if custom_id.endswith(f"{interaction.user.id}"):
            if data.clear == 2:
                if data.player_coin >= 20000:
                    cash = data.sokaikun_coin
                    data.player_coin -= 20000
                    data.sokaikun_coin = data.player_coin
                    data.player_coin = cash
                    data.step = now_step
                    await interaction.response.send_message("「まいどあり！チートコードが適用されたよ！」")
                else:
                    data.step = now_step
                    await interaction.response.send_message("「手持ちコインが足りないよ。」", ephemeral=True)
            else:
                data.step = now_step
                await interaction.response.send_message("「今はその段階じゃないよ。」", ephemeral=True)
        else:
            data.step = now_step
            await interaction.response.send_message("「これはキミ用のボタンじゃないよ。」", ephemeral=True)


# ==========================================
# ミニゲーム用関数
# ==========================================
async def death_check(interaction):
    # 正しいボタンのみ認識させる
    custom_id = interaction.data["custom_id"]
    user_id = interaction.user.id
    data = savedata[user_id]
    check_step = f"death_{data.step}"

    if custom_id.endswith(f"{interaction.user.id}"):
        if data.step == 10:
            await interaction.response.send_message("「処理中だよ。ちょっと待ってね。」", ephemeral=True)
            return False
        else:
            if custom_id.startswith(check_step):
                return True
            else:
                await interaction.response.send_message("「今はその段階じゃないよ。」", ephemeral=True)
                return False
    else:
        await interaction.response.send_message("「これはキミ用のボタンじゃないよ。」", ephemeral=True)
        return False


async def death_stage1_rule(interaction):
    user_id = interaction.user.id
    data = savedata[user_id]
    data.step = 10
    data.sokaikun_coin = 65533
    data.player_coin = 1
    data.table_coin = 1
    data.borrow_coin = 0

    await interaction.response.send_message("「オーケー！それじゃ、ゲームのルールを説明するね。」\n"
        "「このゲームは全部で3つのステージから成り立っているよ！」\n"
        "「ステージ1はステージ2の準備みたいなもので、勝っても負けてもいい。」\n"
        "「ステージ2に勝つことができたらステージ3に進めるよ！」\n"
        "「そして、キミの最終目的はステージ3をクリアすること！」\n"
        "「各ステージのルールは以下にまとめておくね。」")
    rule_stage1_embed = discord.Embed(title="ステージ1: コラッツレイズ",
        description="ボクは65534枚のコインを持っている。"
        "ボクが手持ちコインのうち1枚をテーブルの上に置き、キミは残りの65533枚以下でボクからコインを借りてゲームを開始する。"
        "借りられなかった残り分はボクの手持ちコインとなる。"
        "ボクを先手とし、テーブルのコインに対して交互に①②③のどれかを行う。"
        "ただし、テーブルのコインを0枚にするような操作はできない。\n\n"
        "①レイズ: テーブルにあるコインとピッタリ同じ数のコインを手持ちのコインからテーブルに追加する\n"
        "②カット: テーブルにあるコインから1枚を取り、さらに残ったコインのピッタリ3分の2を取る\n"
        "③レイズ&ギブ: テーブルにあるコインとピッタリ同じ数のコインを手持ちのコインからテーブルに追加し、"
        "さらにその後テーブルにあるコインとピッタリ同じ数のコインを手持ちのコインから相手にあげる\n\n"
        "①②③のどれかを可能な限り行い、先にどれも行えなくなった方が負け。勝敗決定はルールによるもののみで、降参はなし。\n\n",
        color=discord.Color.green())
    await interaction.channel.send(embed=rule_stage1_embed)
    rule_stage2_embed = discord.Embed(title="ステージ2: カウントダウンゲーム",
        description="ステージ1の終了時点でテーブルに置かれていたコインをそのまま使用する。"
        "ゲーム1の勝者を先手としてテーブルの上から交互に1〜3枚ずつコインを取り、最後の1枚を相手に取らせたら勝ち。",
        color=discord.Color.green())
    await interaction.channel.send(embed=rule_stage2_embed)
    if data.clear >= 1:
        rule_stage3_embed = discord.Embed(title="ステージ3: 返済",
            description="ステージ2に勝ったら挑戦できる。"
            "ステージ1で借りたコインの枚数だけ、キミの手持ちコインからボクにコインを返せればクリア。",
            color=discord.Color.green())
        await interaction.channel.send(embed=rule_stage3_embed)
    else:
        rule_stage3_embed = discord.Embed(title="ステージ3: ???",
            description="ステージ2に勝ったら挑戦できる。"
            "ルールおよびクリア条件はまだ明かされない。",
            color=discord.Color.green())
        await interaction.channel.send(embed=rule_stage3_embed)
        await interaction.channel.send("「ステージ3のルールは、キミが一度でもステージ2でボクに勝ったら教えてあげるよ。」\n"
            "「まあ、説明するまでもないようなことなんだけどね。」")
    await interaction.channel.send("「ちなみに、/resetで今のこの状況に戻ってくることができるよ。」\n"
        "「騒がしくしないよう、このスレッド内で使ってね。」\n"
        "「それじゃあテーブルに1枚だけコインを置くよ。」\n"
        "「コインの所持状況はいつでも、/coinで確認できるからね！」\n"
        "「さっそく、ステージ1を始めよっか？」")
    death_stage1_start_embed = discord.Embed(title="何枚借りる？", color=discord.Color.blue())
    data.step = 2
    await interaction.channel.send(embed=death_stage1_start_embed, view=death_2_View(user_id=interaction.user.id))


async def death_stage1_sokaikun(interaction):
    user_id = interaction.user.id
    data = savedata[user_id]

    await interaction.followup.send(f"「テーブルのコインは{data.table_coin}枚だね。」")
    if data.table_coin == 2 and data.sokaikun_coin >= 7:
        await raiseandgive_sokaikun(interaction)
    else:
        if data.table_coin % 3 != 1 or data.table_coin == 1:
            if data.table_coin > data.sokaikun_coin:
                await death_stage1_lose(interaction)
            else:
                await raise_sokaikun(interaction)
        else:
            if data.table_coin > data.sokaikun_coin:
                await cut_sokaikun(interaction)
            else:
                await decide_sokaikun(interaction)


async def decide_sokaikun(interaction):
    user_id = interaction.user.id
    data = savedata[user_id]

    if data.table_coin == 16:
        if data.sokaikun_coin >= 21840:
            await raise_sokaikun(interaction)
        else:
            await cut_sokaikun(interaction)
    elif data.table_coin == 10:
        await cut_sokaikun(interaction)
    else:
        await raise_sokaikun(interaction)


async def death_stage1_player(interaction, choice):
    user_id = interaction.user.id
    data = savedata[user_id]

    if choice == "raise":
        if data.table_coin > data.player_coin:
            await interaction.followup.send("「手持ちのコインが足りないよ。」", ephemeral=True)
            data.step = 4
        else:
            data.player_coin -= data.table_coin
            data.table_coin *= 2
            await interaction.followup.send("[レイズ]しました。")
            await death_stage1_sokaikun(interaction)
    elif choice == "cut":
        if data.table_coin % 3 != 1 or data.table_coin ==1:
            await interaction.followup.send("「テーブルのコイン数が適切じゃないよ。」", ephemeral=True)
            data.step = 4
        else:
            data.player_coin += 1 + (data.table_coin-1)*2//3
            data.table_coin = (data.table_coin-1)//3
            await interaction.followup.send("[カット]しました。")
            await death_stage1_sokaikun(interaction)
    elif choice == "raiseandgive":
        if 3*data.table_coin > data.player_coin:
            await interaction.followup.send("「手持ちのコインが足りないよ。」", ephemeral=True)
            data.step = 4
        else:
            data.sokaikun_coin += data.table_coin*2
            data.player_coin -= data.table_coin*3
            data.table_coin *= 2
            await interaction.followup.send("[レイズ&ギブ]しました。")
            await death_stage1_sokaikun(interaction)


async def raise_sokaikun(interaction):
    user_id = interaction.user.id
    data = savedata[user_id]

    await interaction.channel.send("「ボクは[レイズ]するよ。」")
    data.sokaikun_coin -= data.table_coin
    data.table_coin *= 2
    await death_stage1_check(interaction)


async def cut_sokaikun(interaction):
    user_id = interaction.user.id
    data = savedata[user_id]

    await interaction.channel.send("「ボクは[カット]するね。」")
    data.sokaikun_coin += 1 + (data.table_coin-1)*2//3
    data.table_coin = (data.table_coin-1)//3
    await death_stage1_check(interaction)


async def raiseandgive_sokaikun(interaction):
    user_id = interaction.user.id
    data = savedata[user_id]

    await interaction.channel.send("「…………[レイズ&ギブ]。」")
    data.sokaikun_coin -= data.table_coin*3
    data.player_coin += data.table_coin*2
    data.table_coin *= 2
    await death_stage1_check(interaction)


async def death_stage1_check(interaction):
    user_id = interaction.user.id
    data = savedata[user_id]

    await interaction.channel.send(f"「テーブルのコインは{data.table_coin}枚だよ。」")
    if data.table_coin % 3 != 1 or data.table_coin == 1:
        if data.table_coin > data.player_coin:
            await death_stage1_win(interaction)
            return
    await interaction.channel.send("「さあ、キミの番だね。」")
    death_stage1_embed = discord.Embed(title=f"テーブルのコイン: {data.table_coin}枚\nキミのコイン: {data.player_coin}枚", color=discord.Color.blue())
    data.step = 4
    await interaction.channel.send(embed=death_stage1_embed, view=death_4_View(user_id=interaction.user.id))


async def death_stage1_win(interaction):
    user_id = interaction.user.id
    data = savedata[user_id]

    await asyncio.sleep(0.3)
    await interaction.channel.send("「キミができる操作は無いね。ボクの勝ち！」")
    await asyncio.sleep(0.3)
    await interaction.channel.send("「ボクの先手でステージ2を始めるよ。」")
    await asyncio.sleep(0.3)
    death_stage2_winstart_embed = discord.Embed(title="準備はできた？", color=discord.Color.blue())
    data.step = 5
    await interaction.channel.send(embed=death_stage2_winstart_embed, view=death_5_View(user_id=interaction.user.id))


async def death_stage1_lose(interaction):
    user_id = interaction.user.id
    data = savedata[user_id]

    await asyncio.sleep(0.3)
    await interaction.channel.send("「できる操作が無くなっちゃった。キミの勝ち！」")
    await asyncio.sleep(0.3)
    await interaction.channel.send("「キミの先手でステージ2を始めるよ。」")
    await asyncio.sleep(0.3)
    death_stage2_losestart_embed = discord.Embed(title="準備はできた？", color=discord.Color.blue())
    data.step = 6
    await interaction.channel.send(embed=death_stage2_losestart_embed, view=death_6_View(user_id=interaction.user.id))


async def death_stage2_check(interaction):
    user_id = interaction.user.id
    data = savedata[user_id]

    if data.table_coin == 0:
        await death_stage2_giveup(interaction)
    else:
        await death_stage2_sokaikun(interaction)


async def death_stage2_sokaikun(interaction):
    user_id = interaction.user.id
    data = savedata[user_id]

    await interaction.followup.send(f"「テーブルのコインは{data.table_coin}枚だね。」")
    if data.table_coin == 1:
        data.sokaikun_coin += 1
        data.table_coin = 0
        await death_stage2_result(interaction)
    elif data.table_coin % 4 == 1:
        data.sokaikun_coin += 3
        data.table_coin -= 3
        await interaction.channel.send("「ボクは3枚とるよ。」\n"
            "「もしキミがこのステージの必勝法を知っているなら、結果まで飛ばしてもいいからね。」\n"
            "「その場合、ボクはテーブルから3枚とり続けるよ。」")
        death_stage2_good_embed = discord.Embed(title=f"テーブルのコイン: {data.table_coin}枚", color=discord.Color.blue())
        data.step = 7
        await interaction.channel.send(embed=death_stage2_good_embed, view=death_7_GoodView(user_id=interaction.user.id))
    else:
        data.sokaikun_coin += (data.table_coin+3) % 4
        await interaction.channel.send(f"「ボクは{(data.table_coin+3) % 4}枚とるよ。」\n"
            "「この時点でボクが勝つことは確定しているけど、まだ続ける？」")
        data.table_coin -= (data.table_coin+3) % 4
        death_stage2_bad_embed = discord.Embed(title=f"テーブルのコイン: {data.table_coin}枚", color=discord.Color.blue())
        data.step = 7
        await interaction.channel.send(embed=death_stage2_bad_embed, view=death_7_BadView(user_id=interaction.user.id))


async def death_stage2_player(interaction, choice):
    user_id = interaction.user.id
    data = savedata[user_id]

    if data.table_coin < choice:
        data.step = 7
        await interaction.followup.send("「テーブルのコインが足りないよ。」", ephemeral=True)
    else:
        data.player_coin += choice
        data.table_coin -= choice
        await death_stage2_check(interaction)


async def death_stage2_result(interaction):
    user_id = interaction.user.id
    data = savedata[user_id]

    await asyncio.sleep(0.3)
    await interaction.channel.send("「ボクが最後の1枚をとって、キミの勝ち！」")
    if data.clear == 0:
        await asyncio.sleep(0.3)
        await interaction.channel.send("「クリアも近いね。ワクワクしてきたよ！」")
    await asyncio.sleep(0.3)
    await interaction.channel.send("「それじゃあステージ3を始めようか。」")
    await asyncio.sleep(0.3)
    await interaction.channel.send("「ステージ3のルールはこれだよ！」")
    await asyncio.sleep(0.3)
    rule_stage3_explain_embed = discord.Embed(title="ステージ3: 返済",
    description="ステージ2に勝ったら挑戦できる。"
        "ステージ1で借りたコインの枚数だけ、キミの手持ちコインからボクにコインを返せればクリア。",
        color=discord.Color.green())
    await interaction.channel.send(embed=rule_stage3_explain_embed)
    if data.clear == 0:
        data.clear = 1
        await asyncio.sleep(0.3)
        await interaction.channel.send("「……拍子抜けしたでしょ？」")
        await asyncio.sleep(0.3)
        await interaction.channel.send("「借りたものを返すなんて、わざわざルールに書くまでもないよね。」")
        await asyncio.sleep(0.3)
        await interaction.channel.send("## 「だって当たり前のことだもんね！」")
        await interaction.channel.send(file=discord.File(R"illust/dekaibokudayo.png"))
    await asyncio.sleep(0.3)
    await interaction.channel.send(f"「それじゃあ、ステージ1でキミに貸した{data.borrow_coin}枚の{interaction.user.name}コイン、」")
    await asyncio.sleep(0.3)
    await interaction.channel.send("「耳をそろえて返してよ！」")
    await interaction.channel.send(file=discord.File(R"illust/misebirakashi.png"))
    await asyncio.sleep(0.3)
    death_stage3_return_embed = discord.Embed(title="返してくれる？", color=discord.Color.blue())
    data.step = 8
    await interaction.channel.send(embed=death_stage3_return_embed, view=death_8_View(user_id=interaction.user.id))


async def death_stage2_giveup(interaction):
    user_id = interaction.user.id
    data = savedata[user_id]

    await asyncio.sleep(0.3)
    await interaction.followup.send("「キミが最後の1枚をとったから、ボクの勝ち！」")
    await asyncio.sleep(0.3)
    await interaction.channel.send("「ステージ3には進めないよ。残念だったね。」")
    await asyncio.sleep(0.3)
    await interaction.channel.send("「まだやる気があるなら、/resetで最初からやり直す？」")
    await asyncio.sleep(0.3)
    death_reset_embed = discord.Embed(title="やり直す？", color=discord.Color.red())
    data.step = 9
    await interaction.channel.send(embed=death_reset_embed, view=death_reset_View(user_id=interaction.user.id))


# ==========================================
# ミニゲーム用コマンド
# ==========================================
@bot.tree.command(name='game', description='Sokaikunとゲームができます。実行はDMやミュート推奨で。')
async def game(interaction: discord.Interaction):
    await interaction.response.send_message("オーケー！", ephemeral=True)
    await interaction.channel.send(embed=discord.Embed(title="ゲームを始める？", color=discord.Color.red()), view=yattare_View())


@bot.tree.command(name='coin', description='手持ちコインの状況を確認します。')
async def coin(interaction: discord.Interaction):
    data = savedata[interaction.user.id]
    if data.step >= 1:
        coin_message = f"手持ちコイン: {data.player_coin} (借りたコイン: {data.borrow_coin})\nSokaikunの手持ちコイン: {data.sokaikun_coin}"
        if data.clear == 2:
            if data.borrow_coin == 0 and data.player_coin > data.hi_score:
                data.hi_score = data.player_coin
                await interaction.response.send_message("「ハイスコアを更新したよ！」")
                await interaction.channel.send(coin_message.replace(" (借りたコイン: 0)", "") + f"\nクリア済☆\nHi Score: {data.hi_score}")
            else:
                await interaction.response.send_message(coin_message.replace(" (借りたコイン: 0)", "") + f"\nクリア済☆\nHi Score: {data.hi_score}")
        else:
            await interaction.response.send_message(coin_message.replace(" (借りたコイン: 0)", ""))
    else:
        await interaction.response.send_message("「/gameで始められるゲームで使うコマンドだよ！」", ephemeral=True)


@bot.tree.command(name='reset', description='状況をリセットしてルール説明までもどります。')
async def reset(interaction: discord.Interaction):
    data = savedata[interaction.user.id]
    if data.step >= 1:
        await death_stage1_rule(interaction)
    else:
        await interaction.response.send_message("「/gameで始められるゲームで使うコマンドだよ！」", ephemeral=True)


@bot.tree.command(name='shop', description='sokaiyaを呼び出します。')
async def shop(interaction: discord.Interaction):
    data = savedata[interaction.user.id]
    if data.step >= 1:
        if data.clear == 2:
            await interaction.response.send_message("「いらっしゃい！」", ephemeral=True)
            shop_embed = discord.Embed(title="なにか買っていく？", description="代金は購入時にキミの手持ちコインから引かれるよ。もらった代金はSokaiya金庫に保管するからボクの手持ちコインが増えたりはしないよ。Sokaiyaの利用状況は/resetのたびにリセットされるから、安心してじゃんじゃん買っていってね！", color=discord.Color.red())
            shop_embed.add_field(name="①ハイスコアチャレンジのルール　0コイン", value="クリア後限定、ハイスコアチャレンジのルール説明をする。")
            shop_embed.add_field(name="②Sokaikunアルゴリズム解説書　0コイン", value="ステージ1でのボクの行動選択アルゴリズムが分かる。\n\n")
            shop_embed.add_field(name="③チートコード　20000コイン", value="購入した直後に使用される。キミとボクの手持ちコインを入れ替える。借りたコインの枚数は変化しない。")
            await interaction.channel.send(embed=shop_embed, view=death_shop_View(user_id=interaction.user.id))
        else:
            await interaction.response.send_message("「これはゲームクリア後のコマンドだよ！」", ephemeral=True)
    else:
        await interaction.response.send_message("「/gameで始められるゲームで使うコマンドだよ！」", ephemeral=True)


# ==========================================
# 起動処理
# ==========================================
TOKEN = os.getenv("DISCORD_TOKEN")
# Web サーバの立ち上げ
keep_alive()
bot.run(TOKEN)
