import discord
from discord.ext import commands
from discord import app_commands
from discord import Interaction
from typing import Optional
import datetime
import random
import re
import numpy as np
import os
from keep_alive import keep_alive
import asyncio
from collections import defaultdict


intents = discord.Intents.all()
client = discord.Client(intents=intents) 
tree = app_commands.CommandTree(client)


# 起動時
@client.event
async def on_ready():
    try:
        global savedata
        savedata = defaultdict(lambda: [0, 0, 0, 65535, 0, 0, 0])    #[step, clear, hi_score, sokaikun, coin, table, borrow]
        await tree.sync(guild=None)
        print("コマンドが正常に同期されました。")
    except Exception as e:
        print(f"コマンドの同期中にエラーが発生しました: {e}")
    while True:
        await change_activity()


async def change_activity():
    activity = random.choice(
        ["🍣", "♟️", "💿", "🥜", "🎴", "🀄", "🃏", "👻", "🐑",
         "🦕", "🎲", "🛕", "🎆", "🪺", "🏝️", "💎", "🐢", "🪐",
         "🐘", "🐺", "⚗️", "🧑‍🌾", "🦙", "💀", "🕵️", "💣", "👨‍🦲",
         "🫅", "🫅", "🐧", "💍", "🤖", "🚂", "🍀", "🥯", "🍰",
         "🧰", "🛣️", "🥒", "🌌", "🕷️", "🎪", "⚡", "🏔️", "🌳",
         "🏪", "🏰", "🏀", "🧙‍♂️", "🎣", "🐵", "🔪", "🍛", "🤞",
         "🪬", "💰", "👑", "👁️", "🔍", "☣️", "🚫", "󠁧󠁢󠁳󠁣🏴󠁧󠁢󠁳󠁣󠁴󠁿", "󠁧󠁢󠁷󠁬🎞️"]
    )
    await client.change_presence(activity=discord.Game(activity))
    await asyncio.sleep(10000)


async def kaigizyou_comment():
  comment_list = ["スレッドを作成したよ！",
                  "会議場へようこそ！",
                  "テキチャ勢も参加ありがとう！",
                  "良いアイデアの気配……！",
                  "今日はどんな議題が挙がったのかな？",
                  "本総会のメインチャットはこちら！",
                  "っ🫖 🍵🍵🍵",
                  '*"未来とは、今である。"*\n-# マーガレット・ミード']
  weight_list = [15, 15, 15, 15, 15, 15, 5, 5]
  comment = random.choices(comment_list, weights=weight_list)[0]
  return comment


async def fukuonsei_comment():
  zodiac_list = ['おひつじ座','おうし座','ふたご座','かに座','しし座','おとめ座','てんびん座','さそり座','いて座','やぎ座','みずがめ座','うお座']
  boardgame_list = ['パッチワーク','花火','スシゴー','こねこばくはつ','AZUL','宝石の煌き','それはオレの牧場だ！','スーパーメガラッキーボックス','ニムト','ドブル','SKULL','JUST ONE']
  trpg_list = ['CoC','シノビガミ','ソード・ワールド','フィアスコ','怪談白物語','サタスペ','ダブルクロス','ゆうやけこやけ','パラノイア','アリアンロッド']
  comment_list = ["ハロー、ここは総会ふくおんせいスレッド。",
                  "アイデアをどんどん膨らませよう！",
                  f"今日の1位は……\n## {random.choice(['おめでとう！','すご～い！','やったね♪'])}✨{random.choice(zodiac_list)}のキミ✨\nラッキーボドゲは「{random.choice(boardgame_list)}」だよ！",
                  f"今日の12位は……\n## {random.choice(['残念！','ごめんなさ～い、','あらら。。。'])}💥{random.choice(zodiac_list)}のキミ💥\nでも大丈夫！ラッキーTRPGの「{random.choice(trpg_list)}」をやってハッピーに過ごそう！",
                  "Hello, Fukuonsei-Thread!",
                  "っ🫖 🍵🍵🍵",
                  "一方そのころ、ロシアでは……",
                  "ドーモ。チェス研民=サン。Sokaikunです。",
                  f"しりとり、……{random.choice(['りんご！','量子コンピュータ！','リヴァイアサン！'])}",
                  "{いい感じに盛り上がるコメントを入力}",
                  "*雑談。つまり、くだらない話だから価値がある。有益な話なら、本屋で本を買えばいい。*\n-# 星 新一",
                  f"@here\n# 激レア！今日はハッピーデイ🍀"]
  weight_list = [15, 15, 17, 17, 5, 5, 5, 5, 5, 5, 5, 1]
  comment = random.choices(comment_list, weights=weight_list)[0]
  return comment


# テスト用コマンド
@tree.command(name="hello", description="Say hello to the world!") 
async def hello(interaction: discord.Interaction): 
  await interaction.response.send_message("Hello, World!")


# 説明
@tree.command(name="info_sokaikun", description="Sokaikunについて説明します。")
async def info_sokaikun(interaction: discord.Interaction):
  await interaction.response.send_message(
      "# チェス研総会管理bot [Sokaikun]について\n"
      "## はじめに\n"
      "Sokaikunはichikiyoが作成したチェス研究会用のDiscordBotです。"
      "GitHubにアップロードしたソースコードをRender, UptimeRobot, GoogleAppsScriptによって常時起動しているため、"
      "それらのサイトやDiscord自体の変更によって機能停止する場合があることをご了承ください。\n"
      "サーバーでのコマンド実行が主な機能ですが、一部のコマンドはSokaikunへのDMでも実行可能です。\n"
      "## 必要なセットアップ\n"
      "Sokaikunに管理者権限を与えてサーバーに招待したら、それぞれロール名が 参加者 , 委任者 , 委任宣言者 , 会議場係 , ふくおんせい係 である5つのロールを作成し、"
      "Sokaikunのロールをそれらより上位に設定してください。"
      "また、総会を行うボイスチャンネルの名前は 総会 としておいてください。\n"
      "## コマンド\n"
      "- **/hello** [DMでも実行可能]\n"
      "Hello, World!と返します。テスト用コマンドです。"
      "原因不明のエラーが出た時など、Sokaikunが動作しているかを確かめるためにも使えます。\n"
      "- **/info_sokaikun** [DMでも実行可能]\n"
      "このメッセージを返します。コマンドの説明を出すのに便利です。\n"
      "- **/dice** [DMでも実行可能]\n"
      "引数にダイスコマンドを入れるとダイスを振ります。"
      "◯d◯、◯d◯+◯、◯d◯+◯+◯d◯など、ダイスコマンドや数値同士の加算も可能です。"
      "減算は実装されていませんが、1d3+-1のようにマイナスの数値を足すことはできます。\n"
      "- **/game** [DMでも実行可能]\n"
      "Sokaikunとのゲームを始めるボタンを生成します。2026年のエイプリルフールで実装された機能です。\n"
      "- **/del** [管理者のみ実行可能]\n"
      "委任の宣言・解除を行うボタンを作成します。"
      "[委任宣言者]という名前のロールに対応するボタンが作成されます。"
      "次回総会を委任予定の人はボタン[委任]を押してください。委任票は参加者へランダムに振り分けられます。"
      "但し、特定の人物に票を委任したい場合はボタンを押さずに一般チャンネルへ書き込んでください。\n"
      "- **/sokai_1** [管理者のみ実行可能]\n"
      "ボイスチャンネル 総会 に接続しているメンバーを取得し、参加者一覧として表示します。"
      "また、その時点での委任宣言者ロールの保有者数を委任票として、参加者へランダムに振り分けます。"
      "獲得した委任票の数は参加者一覧の名前横に (+◯) の形で表示され、その数が余分に獲得した投票数となります。"
      "獲得した委任票が0票の場合は名前横に何も表示されません。"
      "このコマンドを実行後、 [参加者ロール保有者] = [ボイスチャンネル#総会に接続していたメンバー] となります。\n"
      "- **/sokai_2** [管理者のみ実行可能]\n"
      "委任宣言者ロール保有者を取得し、委任者一覧として表示します。"
      "このコマンドを実行後、 [委任者ロール保有者] = [元委任宣言者ロール保有者] , [委任宣言者ロール保有者] = [なし] となります。\n"
      "**/sokai_1**および**/sokai_2**は、特定の人物への名指し委任があった場合を想定して分離されています。"
      "**/sokai_1**を実行後、名指しで委任を行った委任者に手動で委任宣言者ロールを付与し、**/sokai_2**を実行してください。"
      "名指しの委任は参加者一覧に計上できないため、各自で確認する必要があります。\n"
      "- **/sokai_3** [管理者のみ実行可能]\n"
      "Sokaikun自身にロール[会議場係], [ふくおんせい係]が付与されているかを確認し、付与されているロールに応じてスレッド[会議場], [ふくおんせい]を作成します。"
      "どちらのロールも付与されていない場合は無効となります。\n"
      "- **/sokai_all** [管理者のみ実行可能]\n"
      "**/sokai_1**, **/sokai_2**, **/sokai_3**をつなげて使用できるコマンドです。"
      "名指しの委任が無かった場合、すなわち全員が**/del**のボタンで委任を宣言した場合にはこのコマンドを使用してください。\n"
      "## おわりに\n"
      "このBotを作るにあたって、ichikiyoはいろんなところからコードをパクってきました。"
      "Python弱者がブラックボックスをブラックボックスのまま合成したキメラがSokaikunです。"
      "「なんか挙動がおかしいな」と思ったあなたの感覚は正しいかもしれませんので、臆せず意見を寄せてください。"
      "暇だったら直します。"
  )


# ダイスボット
@tree.command(name="dice", description="ダイスを振ります。")
async def dice(interaction: discord.Interaction, ダイス: str):
  if interaction.user.bot:
      return 
  content = ダイス
  splitPlus = content.split('+')
  formatedContent = content.replace(' ', '').replace('+', ' + ')        
  response = formatedContent + ": "
  result = 0
  for (i, context) in enumerate(splitPlus):
      splited = context.split('d')
      if len(splited) == 1:
          result = result + int(splited[0])
          response = response + splited[0]
      else:
          for dice in range(int(splited[0])):
              res = np.random.randint(1, (int(splited[1])+1))
              result = result + res
              response = response + str(res)
              # ダイスが1個以上の時
              if not (int(splited[0]) == 1):
                  # 最後のダイスじゃない時
                  if not ((dice == (int(splited[0]) - 1))):            
                      response = response + " + "
                  # 最後のダイスかつ、ダイスセットが１つだけの時
                  elif (dice == int(splited[0]) - 1) and (len(splitPlus) == 1):
                      response = response + " = " + str(result)
      # ダイスセットが1個以上の時
      if not (len(splitPlus) == 1):
          # 最後のダイスセットじゃない時
          if not (i == (len(splitPlus) - 1)):
              response = response + " + "
          # 最後のダイスセットの時
          elif (i == len(splitPlus) - 1):
              response = response + " = " + str(result)
  await interaction.response.send_message(response)


# 総会、委任関係
@tree.command(name="del", description="委任宣言開始 要管理者権限")
@discord.app_commands.guild_only()
@discord.app_commands.default_permissions(administrator=True)
async def delpanel(interaction: Interaction):
  warning_embed = discord.Embed(
      description="委任を開始しました！",
      color=discord.Color.green(),
  )
  await interaction.response.send_message(embed=warning_embed)
  del_embed = discord.Embed(title="総会の委任はこちらから", description="特定の人物に委任したい場合は、ボタンを押さずに一般チャンネルへその旨を記載してください", color=discord.Color.green())
  del_on_button = discord.ui.Button(style=discord.ButtonStyle.primary, custom_id="del_on_id", label="委任")
  del_off_button = discord.ui.Button(style=discord.ButtonStyle.danger, custom_id="del_off_id", label="取消")
  view = discord.ui.View()
  view.add_item(del_on_button)
  view.add_item(del_off_button)
  await interaction.channel.send(embed=del_embed, view=view)


@tree.command(name="sokai_1", description="総会Step1 参加者更新&委任票集計 要管理者権限")
@discord.app_commands.guild_only()
@discord.app_commands.default_permissions(administrator=True)
async def sokai_1(interaction: Interaction):
  await interaction.response.defer(thinking=True)  
  sokai_vc = discord.utils.get(interaction.guild.voice_channels, name = "総会")
  DIFF_JST_FROM_UTC = 9
  now = datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=DIFF_JST_FROM_UTC)
  now_date = now.date()
  if sokai_vc.members == []:
      await interaction.followup.send("エラー: ボイスチャンネル[総会]に誰もいません。", ephemeral=True)
      return
  del_role = discord.utils.get(interaction.guild.roles, name = "委任宣言者")
  if del_role == None:
      await interaction.followup.send("エラー: ロール[委任宣言者]を見つけられませんでした。", ephemeral=True)
      return
  pre_role = discord.utils.get(interaction.guild.roles, name = "参加者")
  if pre_role:
      for i in pre_role.members:
          try:
              await i.remove_roles(pre_role)
          except discord.Forbidden:
              await interaction.followup.send("エラー: ロールを削除できません。権限が不足している可能性があります。", ephemeral=True)
              return
  else:
      await interaction.followup.send("エラー: ロール[参加者]を見つけられませんでした。", ephemeral=True)
      return
  sokai_1_message = f"{now_date}　総会\n### 参加者\n"
  del_member = del_role.members
  pre_member = sokai_vc.members
  pre_member_name = sorted([i.display_name for i in pre_member])
  del_number = [0]*len(pre_member)
  del_number_index = random.choices(range(len(pre_member)), k = len(del_member))
  for i in del_number_index:
      del_number[i] += 1
  sokai_1_message += "、".join([pre_member_name[i] + f"(+{str(del_number[i])})" for i in range(len(pre_member))])
  for i in pre_member:
      try:
          await i.add_roles(pre_role)
      except discord.Forbidden:
          await interaction.followup.send("エラー: ロールを付与できません。権限が不足している可能性があります。", ephemeral=True)
          return
  await interaction.followup.send(sokai_1_message.replace("(+0)", ""))


@tree.command(name="sokai_2", description="総会Step2 委任者更新 要管理者権限")
@discord.app_commands.guild_only()
@discord.app_commands.default_permissions(administrator=True)
async def sokai_2(interaction: Interaction):
  await interaction.response.defer(thinking=True)
  sokai_vc = discord.utils.get(interaction.guild.voice_channels, name = "総会")
  if sokai_vc.members == []:
      await interaction.followup.send("エラー: ボイスチャンネル[総会]に誰もいません。", ephemeral=True)
      return
  del_role = discord.utils.get(interaction.guild.roles, name = "委任宣言者")
  if del_role == None:
      await interaction.followup.send("エラー: ロール[委任宣言者]を見つけられませんでした。", ephemeral=True)
      return
  deled_role = discord.utils.get(interaction.guild.roles, name = "委任者")
  if deled_role:
      for i in deled_role.members:
          try:
              await i.remove_roles(discord.Object(int(deled_role.id)))
          except discord.Forbidden:
              await interaction.followup.send("エラー: ロールを削除できません。権限が不足している可能性があります。", ephemeral=True)
              return
  for i in del_role.members:
      try:
          await i.add_roles(deled_role)
          await i.remove_roles(discord.Object(int(del_role.id)))
      except discord.Forbidden:
          await interaction.followup.send("エラー: ロールを付与または削除できません。権限が不足している可能性があります。", ephemeral=True)
          return
  new_deled_role = discord.utils.get(interaction.guild.roles, name = "委任者")
  new_deled_role_name = sorted([i.display_name for i in new_deled_role.members])
  sokai_2_message = "### 委任者\n"
  sokai_2_message += "、".join(new_deled_role_name)
  await interaction.followup.send(sokai_2_message)


@tree.command(name="sokai_3", description="総会Step3 総会用スレッド作成 要管理者権限")
@discord.app_commands.guild_only()
@discord.app_commands.default_permissions(administrator=True)
async def sokai_3(interaction: Interaction):
  DIFF_JST_FROM_UTC = 9
  now = datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=DIFF_JST_FROM_UTC)
  now_date = now.date()
  await interaction.response.defer(thinking=True)
  sokaikun = interaction.guild.get_member(1386751629923057827)  #SokaikunのユーザーID
  kaigizyou_role = discord.utils.get(interaction.guild.roles, name = "会議場係")
  fukuonsei_role = discord.utils.get(interaction.guild.roles, name = "ふくおんせい係")
  if not discord.utils.get(sokaikun.roles, id=int(kaigizyou_role.id)) and not discord.utils.get(sokaikun.roles, id=int(fukuonsei_role.id)):
      await interaction.followup.send("ボクはロール[会議場係], [ふくおんせい係]のどちらも持ってないよ！", ephemeral=True)
      return
  sokai_3_message = "テキストチャット用スレッドはこちら\n"
  if discord.utils.get(sokaikun.roles, id=int(kaigizyou_role.id)):
      kaigizyou_thread = await interaction.channel.create_thread(name=f"{now_date} 会議場", type=discord.ChannelType.public_thread)
      await kaigizyou_thread.send(await kaigizyou_comment())
      sokai_3_message += f"{kaigizyou_thread.jump_url}　"
  if discord.utils.get(sokaikun.roles, id=int(fukuonsei_role.id)):
      fukuonsei_thread = await interaction.channel.create_thread(name=f"{now_date} ふくおんせい", type=discord.ChannelType.public_thread)
      await fukuonsei_thread.send(await fukuonsei_comment())
      sokai_3_message += fukuonsei_thread.jump_url
  await interaction.followup.send(sokai_3_message)


@tree.command(name="sokai_all", description="総会Step1～3 要管理者権限")
@discord.app_commands.guild_only()
@discord.app_commands.default_permissions(administrator=True)
async def sokai_all(interaction: Interaction):
  DIFF_JST_FROM_UTC = 9
  now = datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=DIFF_JST_FROM_UTC)
  now_date = now.date()
  await interaction.response.defer(thinking=True)
  sokai_vc = discord.utils.get(interaction.guild.voice_channels, name = "総会")
  if sokai_vc.members == []:
      await interaction.followup.send("エラー: ボイスチャンネル[総会]に誰もいません。", ephemeral=True)
      return
  del_role = discord.utils.get(interaction.guild.roles, name = "委任宣言者")
  if del_role == None:
      await interaction.followup.send("エラー: ロール[委任宣言者]を見つけられませんでした。", ephemeral=True)
      return
  pre_role = discord.utils.get(interaction.guild.roles, name = "参加者")
  if pre_role:
      for i in pre_role.members:
          try:
              await i.remove_roles(discord.Object(int(pre_role.id)))
          except discord.Forbidden:
              await interaction.followup.send("エラー: ロールを削除できません。権限が不足している可能性があります。", ephemeral=True)
              return
  else:
      await interaction.followup.send("エラー: ロール[参加者]を見つけられませんでした。", ephemeral=True)
      return
  deled_role = discord.utils.get(interaction.guild.roles, name = "委任者")
  if deled_role:
      for i in deled_role.members:
          try:
              await i.remove_roles(discord.Object(int(deled_role.id)))
          except discord.Forbidden:
              await interaction.followup.send("エラー: ロールを削除できません。権限が不足している可能性があります。", ephemeral=True)
              return
  sokai_all_message = f"{now_date}　総会\n### 参加者\n"
  del_member = del_role.members
  pre_member = sokai_vc.members
  pre_member_name = sorted([i.display_name for i in pre_member])
  del_number = [0]*len(pre_member)
  del_number_index = random.choices((range(len(pre_member))), k = len(del_member))
  for i in del_number_index:
      del_number[i] += 1
  sokai_all_message += "、".join([pre_member_name[i] + f"(+{str(del_number[i])})" for i in range(len(pre_member))])
  for i in pre_member:
      try:
          await i.add_roles(pre_role)
      except discord.Forbidden:
          await interaction.followup.send("エラー: ロールを付与できません。権限が不足している可能性があります。", ephemeral=True)
          return
  for i in del_role.members:
      try:
          await i.add_roles(deled_role)
          await i.remove_roles(discord.Object(int(del_role.id)))
      except discord.Forbidden:
          await interaction.followup.send("エラー: ロールを付与または削除できません。権限が不足している可能性があります。", ephemeral=True)
          return
  new_deled_role = discord.utils.get(interaction.guild.roles, name = "委任者")
  new_deled_role_name = sorted([i.display_name for i in new_deled_role.members])
  sokai_all_message += "\n### 委任者\n"
  sokai_all_message += "、".join(new_deled_role_name)
  sokaikun = interaction.guild.get_member(1386751629923057827)  #SokaikunのユーザーID
  kaigizyou_role = discord.utils.get(interaction.guild.roles, name = "会議場係")
  fukuonsei_role = discord.utils.get(interaction.guild.roles, name = "ふくおんせい係")
  if not discord.utils.get(sokaikun.roles, id=int(kaigizyou_role.id)) and not discord.utils.get(sokaikun.roles, id=int(fukuonsei_role.id)):
      await interaction.followup.send(sokai_all_message.replace("(+0)", ""))
      return
  sokai_all_message += "\n\nテキストチャット用スレッドはこちら\n"
  if discord.utils.get(sokaikun.roles, id=int(kaigizyou_role.id)):
      kaigizyou_thread = await interaction.channel.create_thread(name=f"{now_date} 会議場", type=discord.ChannelType.public_thread)
      await kaigizyou_thread.send(await kaigizyou_comment())
      sokai_all_message += f"{kaigizyou_thread.jump_url}　"
  if discord.utils.get(sokaikun.roles, id=int(fukuonsei_role.id)):
      fukuonsei_thread = await interaction.channel.create_thread(name=f"{now_date} ふくおんせい", type=discord.ChannelType.public_thread)
      await fukuonsei_thread.send(await fukuonsei_comment())
      sokai_all_message += fukuonsei_thread.jump_url
  await interaction.followup.send(sokai_all_message.replace("(+0)", ""))


@client.event
async def on_interaction(interaction:discord.Interaction):
    try:
        if interaction.data['component_type'] == 2:
            await on_button_click(interaction)
    except KeyError:
        pass


async def on_button_click(interaction):
  custom_id = interaction.data["custom_id"]
  if custom_id == "del_on_id":
      member = interaction.guild.get_member(interaction.user.id)
      try:
          del_message = await interaction.channel.fetch_message(interaction.message.id)
          del_role = discord.utils.get(del_message.guild.roles, name = "委任宣言者")
      except discord.HTTPException as e:
          print(f"Error fetching message: {e}")
          await interaction.response.send_message("エラー: メッセージを取得できませんでした。", ephemeral=True)
          return
      if discord.utils.get(member.roles, id=int(del_role.id)):
          await interaction.response.send_message("ロール[委任宣言者]は既に付与されています。", ephemeral=True)
      else:
          if del_role:
              try:
                  await member.add_roles(del_role)
                  await interaction.response.send_message(f"ロールを付与しました: {del_role.name}", ephemeral=True)
              except discord.Forbidden:
                  await interaction.response.send_message("エラー: ロールを付与できません。権限が不足している可能性があります。", ephemeral=True)
          else:
              await interaction.response.send_message("エラー: ロール[委任宣言者]を見つけられませんでした。", ephemeral=True)
  elif custom_id == "del_off_id":
      member = interaction.guild.get_member(interaction.user.id)
      try:
          del_message = await interaction.channel.fetch_message(interaction.message.id)
          del_role = discord.utils.get(del_message.guild.roles, name = "委任宣言者")
      except discord.HTTPException as e:
          print(f"Error fetching message: {e}")
          await interaction.response.send_message("エラー: メッセージを取得できませんでした。", ephemeral=True)
          return
      if discord.utils.get(member.roles, id=int(del_role.id)):
          try:
              await member.remove_roles(discord.Object(int(del_role.id)))
              await interaction.response.send_message(f"ロールを削除しました: {del_role.name}", ephemeral=True)
          except discord.Forbidden:
              await interaction.response.send_message("エラー: ロールを削除できません。権限が不足している可能性があります。", ephemeral=True)
      else:
          if del_role:
              await interaction.response.send_message("委任は既に解除されています。", ephemeral=True)
          else:
              await interaction.response.send_message("エラー: ロール[委任宣言者]を見つけられませんでした。", ephemeral=True)
  elif custom_id == "yattare_id":
      if savedata[interaction.user.id][0] == 0:
          savedata[interaction.user.id][0] = 10
          await interaction.response.send_message("オーケー！", ephemeral=True)
          try:
              thread = await interaction.channel.create_thread(name=f"{interaction.user.name}とのゲーム", type=discord.ChannelType.private_thread)
              await thread.add_user(interaction.user)
          except:
              thread = interaction.channel
          await thread.send("「ようこそ！ここがキミとのゲームスペースさ！」")
          await asyncio.sleep(3)
          await thread.send(f"「そしてこれが…ゲームにつかう{interaction.user.name}コイン！」")
          await thread.send(file=discord.File(R"illust\kiminocoin.png"))
          await asyncio.sleep(3)
          await thread.send("「当然キミとのゲームに使うためだけに製造したものだよ！」")
          await asyncio.sleep(3)
          await thread.send("「全部で65535枚あるからじゃんじゃん使えるね！」")
          await thread.send(file=discord.File(R"illust\yamamori.png"))
          await asyncio.sleep(3)
          await thread.send("「ゲームの参加賞として、はい！1枚あげる！」")
          savedata[interaction.user.id][3] = 65534
          savedata[interaction.user.id][4] = 1
          await asyncio.sleep(3)
          await thread.send("「/coinで今のコイン所持状況が分かるよ。やってみて！」")
          await asyncio.sleep(3)
          await thread.send("「準備ができたらルール説明を始めるね！」")
          death_rule_embed = discord.Embed(title="準備はできた？", color=discord.Color.blue())
          death_rule_button = discord.ui.Button(style=discord.ButtonStyle.primary, custom_id=f"death_1_id_{interaction.user.id}", label="はい")
          view = discord.ui.View()
          view.add_item(death_rule_button)
          await asyncio.sleep(3)
          savedata[interaction.user.id][0] = 1
          await thread.send(embed=death_rule_embed, view=view)
      else:
          await interaction.response.send_message("もう始まってるよ！やり直したい場合はスレッド内で/resetを使ってね。", ephemeral=True)
  elif custom_id.endswith(f"{interaction.user.id}"):
      if savedata[interaction.user.id][0] == 10:
          await interaction.response.send_message("「処理中だよ。ちょっと待ってね。」", ephemeral=True)
      elif custom_id.startswith("reset"):
          if savedata[interaction.user.id][0] == 0:
              await interaction.response.send_message("「/gameで始められるゲームで使うボタンだよ！」", ephemeral=True)
          else:
              await death_stage1_rule(interaction)
      elif custom_id.startswith("item_1_id"):
          if savedata[interaction.user.id][1] == 2:
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
      elif custom_id.startswith("item_2_id"):
          if savedata[interaction.user.id][1] == 2:
              await interaction.response.send_message("「まいどあり！それじゃあこれをどうぞ！」")
              item_2_embed = discord.Embed(title="Sokaikunアルゴリズム解説書", description="ステージ1でSokaikunに行動選択の余地がある場合、以下のアルゴリズムで行動する。", color=discord.Color.green())
              item_2_embed.add_field(name="1. [レイズ]するパターン", value="下記の「[カット]するパターン」「[レイズ&ギブ]するパターン」のどちらにも当てはまらない場合", inline=False)
              item_2_embed.add_field(name="2. [カット]するパターン", value="パターン①: テーブルのコインが10枚の場合\n"
                  "パターン②: テーブルのコインが16枚、かつSokaikunの手持ちコインが21839枚以下の場合", inline=False)
              item_2_embed.add_field(name="3. [レイズ&ギブ]するパターン", value="テーブルのコインが2枚、かつSokaikunの手持ちコインが7枚以上の場合", inline=False)
              await interaction.channel.send(embed=item_2_embed)
          else:
              await interaction.response.send_message("「今はその段階じゃないよ。」", ephemeral=True)
      elif custom_id.startswith("item_3_id"):
          if savedata[interaction.user.id][1] == 2:
              if savedata[interaction.user.id][4] >= 20000:
                  cash = savedata[interaction.user.id][3]
                  savedata[interaction.user.id][4] -= 20000
                  savedata[interaction.user.id][3] = savedata[interaction.user.id][4]
                  savedata[interaction.user.id][4] = cash
                  await interaction.response.send_message("「まいどあり！チートコードが適用されたよ！」")
              else:
                  await interaction.response.send_message("「手持ちコインが足りないよ。」", ephemeral=True)
          else:
              await interaction.response.send_message("「今はその段階じゃないよ。」", ephemeral=True)
      elif custom_id.startswith("death"):
          check_step = f"death_{savedata[interaction.user.id][0]}"
          if custom_id.startswith(check_step):
              await death_button_click(interaction)
          else:
              await interaction.response.send_message("「今はその段階じゃないよ。」", ephemeral=True)
  else:
      await interaction.response.send_message("「これはキミ用のボタンじゃないよ。」", ephemeral=True)


async def death_button_click(interaction):
  custom_id = interaction.data["custom_id"]
  if custom_id.startswith("death_1_id"):
      savedata[interaction.user.id][0] = 10
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
      if savedata[interaction.user.id][1] >= 1:
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
      savedata[interaction.user.id][3] = 65533
      savedata[interaction.user.id][5] = 1
      await interaction.channel.send(file=discord.File(R"illust\hajimeruka.png"))
      await asyncio.sleep(3)
      await interaction.channel.send("「さっそく、ステージ1を始めよっか？」")
      death_stage1_start_embed = discord.Embed(title="何枚借りる？", color=discord.Color.blue())
      view = discord.ui.View()
      death_stage1_borrow_button = discord.ui.Button(style=discord.ButtonStyle.primary, custom_id=f"death_2_id_{interaction.user.id}", label="入力する")
      view.add_item(death_stage1_borrow_button)
      await asyncio.sleep(3)
      savedata[interaction.user.id][0] = 2
      await interaction.channel.send(embed=death_stage1_start_embed, view=view)
  elif custom_id.startswith("death_2_id"):
      await interaction.response.send_modal(MyModal())
  elif custom_id.startswith("death_3_re_id"):
      await interaction.response.send_modal(MyModal())
  elif custom_id.startswith("death_3_go_id"):
      savedata[interaction.user.id][0] = 10
      await interaction.response.defer(thinking=True)
      await death_stage1_sokaikun(interaction)
  elif custom_id.startswith("death_4_raise_id"):
      savedata[interaction.user.id][0] = 10
      await interaction.response.defer(thinking=True)
      await death_stage1_player(interaction, "raise")
  elif custom_id.startswith("death_4_cut_id"):
      savedata[interaction.user.id][0] = 10
      await interaction.response.defer(thinking=True)
      await death_stage1_player(interaction, "cut")
  elif custom_id.startswith("death_4_raiseandgive_id"):
      savedata[interaction.user.id][0] = 10
      await interaction.response.defer(thinking=True)
      await death_stage1_player(interaction, "raiseandgive")
  elif custom_id.startswith("death_5_id"):
      savedata[interaction.user.id][0] = 10
      await interaction.response.defer(thinking=True)
      await death_stage2_sokaikun(interaction)
  elif custom_id.startswith("death_6_id"):
      savedata[interaction.user.id][0] = 10
      await interaction.response.send_message("「オーケー！まずはキミの番だね！」")
      view = discord.ui.View()
      death_one_button = discord.ui.Button(style=discord.ButtonStyle.primary, custom_id=f"death_7_one_id_{interaction.user.id}", label="1枚とる")
      death_two_button = discord.ui.Button(style=discord.ButtonStyle.primary, custom_id=f"death_7_two_id_{interaction.user.id}", label="2枚とる")
      death_three_button = discord.ui.Button(style=discord.ButtonStyle.primary, custom_id=f"death_7_three_id_{interaction.user.id}", label="3枚とる")
      view.add_item(death_one_button)
      view.add_item(death_two_button)
      view.add_item(death_three_button)
      death_stage2_bad_embed = discord.Embed(title=f"テーブルのコイン: {savedata[interaction.user.id][5]}枚", color=discord.Color.blue())
      savedata[interaction.user.id][0] = 7
      await interaction.channel.send(embed=death_stage2_bad_embed, view=view)
  elif custom_id.startswith("death_7_one_id"):
      savedata[interaction.user.id][0] = 10
      await interaction.response.defer(thinking=True)
      await death_stage2_player(interaction, 1)
  elif custom_id.startswith("death_7_two_id"):
      savedata[interaction.user.id][0] = 10
      await interaction.response.defer(thinking=True)
      await death_stage2_player(interaction, 2)
  elif custom_id.startswith("death_7_three_id"):
      savedata[interaction.user.id][0] = 10
      await interaction.response.defer(thinking=True)
      await death_stage2_player(interaction, 3)
  elif custom_id.startswith("death_7_result_id"):
      savedata[interaction.user.id][0] = 10
      await interaction.response.send_message("「オーケー！それじゃ、結果まで飛ばすよ。」")
      savedata[interaction.user.id][3] += savedata[interaction.user.id][5] // 4 * 3 + 1
      savedata[interaction.user.id][4] += (savedata[interaction.user.id][5]+2) // 4
      savedata[interaction.user.id][5] = 0
      await death_stage2_result(interaction)
  elif custom_id.startswith("death_7_giveup_id"):
      savedata[interaction.user.id][0] = 10
      await interaction.response.send_message("「オーケー！それじゃ、適当に結果まで進めるね。」")
      savedata[interaction.user.id][3] += savedata[interaction.user.id][5] // 4
      savedata[interaction.user.id][4] += savedata[interaction.user.id][5]*3 // 4 + 1
      savedata[interaction.user.id][5] = 0
      await death_stage2_giveup(interaction)
  elif custom_id.startswith("death_8_id"):
      savedata[interaction.user.id][0] = 10
      await interaction.response.defer(thinking=True)
      if savedata[interaction.user.id][4] >= savedata[interaction.user.id][6]:
          savedata[interaction.user.id][3] += savedata[interaction.user.id][6]
          savedata[interaction.user.id][4] -= savedata[interaction.user.id][6]
          await interaction.followup.send(f"「うんうん、ピッタリ{savedata[interaction.user.id][6]}枚。確かに返してもらったよ！」")
          savedata[interaction.user.id][6] = 0
          await asyncio.sleep(3)
          await interaction.channel.send("「キミと遊べて楽しかったよ！付き合ってくれてありがとう！」")
          if savedata[interaction.user.id][1] == 1:
              savedata[interaction.user.id][1] = 2
              await interaction.channel.send(file=discord.File(R"illust\arigatou.png"))
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
          death_reset_embed = discord.Embed(title="やり直す？", color=discord.Color.red())
          view = discord.ui.View()
          death_reset_button = discord.ui.Button(style=discord.ButtonStyle.danger, custom_id=f"reset_{interaction.user.id}", label="/reset")
          view.add_item(death_reset_button)
          await interaction.channel.send(embed=death_reset_embed, view=view)
      savedata[interaction.user.id][0] = 9


async def death_stage1_rule(interaction):
      savedata[interaction.user.id][0] = 10
      savedata[interaction.user.id][3] = 65533
      savedata[interaction.user.id][4] = 1
      savedata[interaction.user.id][5] = 1
      savedata[interaction.user.id][6] = 0
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
      if savedata[interaction.user.id][1] >= 1:
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
      view = discord.ui.View()
      death_stage1_borrow_button = discord.ui.Button(style=discord.ButtonStyle.primary, custom_id=f"death_2_id_{interaction.user.id}", label="入力する")
      view.add_item(death_stage1_borrow_button)
      savedata[interaction.user.id][0] = 2
      await interaction.channel.send(embed=death_stage1_start_embed, view=view)
  

async def death_stage1_sokaikun(interaction):
  await interaction.followup.send(f"「テーブルのコインは{savedata[interaction.user.id][5]}枚だね。」")
  if savedata[interaction.user.id][5] == 2 and savedata[interaction.user.id][3] >= 7:
      await raiseandgive_sokaikun(interaction)
  else:
      if savedata[interaction.user.id][5] % 3 != 1 or savedata[interaction.user.id][5] == 1:
          if savedata[interaction.user.id][5] > savedata[interaction.user.id][3]:
              await death_stage1_lose(interaction)
          else:
              await raise_sokaikun(interaction)
      else:
          if savedata[interaction.user.id][5] > savedata[interaction.user.id][3]:
              await cut_sokaikun(interaction)
          else:
              await decide_sokaikun(interaction)


async def decide_sokaikun(interaction):
  if savedata[interaction.user.id][5] == 16:
      if savedata[interaction.user.id][3] >= 21840:
          await raise_sokaikun(interaction)
      else:
          await cut_sokaikun(interaction)
  elif savedata[interaction.user.id][5] == 10:
      await cut_sokaikun(interaction)
  else:
      await raise_sokaikun(interaction)


async def death_stage1_player(interaction, choice):
  if choice == "raise":
      if savedata[interaction.user.id][5] > savedata[interaction.user.id][4]:
          await interaction.followup.send("「手持ちのコインが足りないよ。」", ephemeral=True)
          savedata[interaction.user.id][0] = 4
      else:
          savedata[interaction.user.id][4] -= savedata[interaction.user.id][5]
          savedata[interaction.user.id][5] *= 2
          await interaction.followup.send("[レイズ]しました。")
          await death_stage1_sokaikun(interaction)
  elif choice == "cut":
      if savedata[interaction.user.id][5] % 3 != 1 or savedata[interaction.user.id][5] ==1:
          await interaction.followup.send("「テーブルのコイン数が適切じゃないよ。」", ephemeral=True)
          savedata[interaction.user.id][0] = 4
      else:
          savedata[interaction.user.id][4] += 1 + (savedata[interaction.user.id][5]-1)*2//3
          savedata[interaction.user.id][5] = (savedata[interaction.user.id][5]-1)//3
          await interaction.followup.send("[カット]しました。")
          await death_stage1_sokaikun(interaction)
  elif choice == "raiseandgive":
      if 3*savedata[interaction.user.id][5] > savedata[interaction.user.id][4]:
          await interaction.followup.send("「手持ちのコインが足りないよ。」", ephemeral=True)
          savedata[interaction.user.id][0] = 4
      else:
          savedata[interaction.user.id][3] += savedata[interaction.user.id][5]*2
          savedata[interaction.user.id][4] -= savedata[interaction.user.id][5]*3
          savedata[interaction.user.id][5] *= 2
          await interaction.followup.send("[レイズ&ギブ]しました。")
          await death_stage1_sokaikun(interaction)


async def raise_sokaikun(interaction):
  await interaction.channel.send("「ボクは[レイズ]するよ。」")
  savedata[interaction.user.id][3] -= savedata[interaction.user.id][5]
  savedata[interaction.user.id][5] *= 2
  await death_stage1_check(interaction)


async def cut_sokaikun(interaction):
  await interaction.channel.send("「ボクは[カット]するね。」")
  savedata[interaction.user.id][3] += 1 + (savedata[interaction.user.id][5]-1)*2//3
  savedata[interaction.user.id][5] = (savedata[interaction.user.id][5]-1)//3
  await death_stage1_check(interaction)


async def raiseandgive_sokaikun(interaction):
  await interaction.channel.send("「…………[レイズ&ギブ]。」")
  savedata[interaction.user.id][3] -= savedata[interaction.user.id][5]*3
  savedata[interaction.user.id][4] += savedata[interaction.user.id][5]*2
  savedata[interaction.user.id][5] *= 2
  await death_stage1_check(interaction)


async def death_stage1_check(interaction):
  await interaction.channel.send(f"「テーブルのコインは{savedata[interaction.user.id][5]}枚だよ。」")
  if savedata[interaction.user.id][5] % 3 != 1 or savedata[interaction.user.id][5] == 1:
      if savedata[interaction.user.id][5] > savedata[interaction.user.id][4]:
          await death_stage1_win(interaction)
          return
  await interaction.channel.send("「さあ、キミの番だね。」")
  view = discord.ui.View()
  death_raise_button = discord.ui.Button(style=discord.ButtonStyle.primary, custom_id=f"death_4_raise_id_{interaction.user.id}", label="レイズ")
  death_cut_button = discord.ui.Button(style=discord.ButtonStyle.primary, custom_id=f"death_4_cut_id_{interaction.user.id}", label="カット")
  death_raiseandgive_button = discord.ui.Button(style=discord.ButtonStyle.primary, custom_id=f"death_4_raiseandgive_id_{interaction.user.id}", label="レイズ&ギブ")
  view.add_item(death_raise_button)
  view.add_item(death_cut_button)
  view.add_item(death_raiseandgive_button)
  death_stage1_embed = discord.Embed(title=f"テーブルのコイン: {savedata[interaction.user.id][5]}枚\nキミのコイン: {savedata[interaction.user.id][4]}枚", color=discord.Color.blue())
  savedata[interaction.user.id][0] = 4
  await interaction.channel.send(embed=death_stage1_embed, view=view)


async def death_stage1_win(interaction):
  await asyncio.sleep(0.3)
  await interaction.channel.send("「キミができる操作は無いね。ボクの勝ち！」")
  await asyncio.sleep(0.3)
  await interaction.channel.send("「ボクの先手でステージ2を始めるよ。」")
  death_stage2_winstart_embed = discord.Embed(title="準備はできた？", color=discord.Color.blue())
  death_stage2_winstart_button = discord.ui.Button(style=discord.ButtonStyle.primary, custom_id=f"death_5_id_{interaction.user.id}", label="はい")
  death_reset_button = discord.ui.Button(style=discord.ButtonStyle.danger, custom_id=f"reset_{interaction.user.id}", label="/reset")
  view = discord.ui.View()
  view.add_item(death_stage2_winstart_button)
  view.add_item(death_reset_button)
  await asyncio.sleep(0.3)
  savedata[interaction.user.id][0] = 5
  await interaction.channel.send(embed=death_stage2_winstart_embed, view=view)


async def death_stage1_lose(interaction):
  await asyncio.sleep(0.3)
  await interaction.channel.send("「できる操作が無くなっちゃった。キミの勝ち！」")
  await asyncio.sleep(0.3)
  await interaction.channel.send("「キミの先手でステージ2を始めるよ。」")
  death_stage2_losestart_embed = discord.Embed(title="準備はできた？", color=discord.Color.blue())
  death_stage2_losestart_button = discord.ui.Button(style=discord.ButtonStyle.primary, custom_id=f"death_6_id_{interaction.user.id}", label="はい")
  death_reset_button = discord.ui.Button(style=discord.ButtonStyle.danger, custom_id=f"reset_{interaction.user.id}", label="/reset")
  view = discord.ui.View()
  view.add_item(death_stage2_losestart_button)
  view.add_item(death_reset_button)
  await asyncio.sleep(0.3)
  savedata[interaction.user.id][0] = 6
  await interaction.channel.send(embed=death_stage2_losestart_embed, view=view)


async def death_stage2_check(interaction):
  if savedata[interaction.user.id][5] == 0:
      await death_stage2_giveup(interaction)
  else:
      await death_stage2_sokaikun(interaction)


async def death_stage2_sokaikun(interaction):
  await interaction.followup.send(f"「テーブルのコインは{savedata[interaction.user.id][5]}枚だね。」")
  if savedata[interaction.user.id][5] == 1:
      savedata[interaction.user.id][3] += 1
      savedata[interaction.user.id][5] = 0
      await death_stage2_result(interaction)
  elif savedata[interaction.user.id][5] % 4 == 1:
      savedata[interaction.user.id][3] += 3
      savedata[interaction.user.id][5] -= 3
      await interaction.channel.send("「ボクは3枚とるよ。」\n"
          "「もしキミがこのステージの必勝法を知っているなら、結果まで飛ばしてもいいからね。」\n"
          "「その場合、ボクはテーブルから3枚とり続けるよ。」")
      view = discord.ui.View()
      death_one_button = discord.ui.Button(style=discord.ButtonStyle.primary, custom_id=f"death_7_one_id_{interaction.user.id}", label="1枚とる")
      death_two_button = discord.ui.Button(style=discord.ButtonStyle.primary, custom_id=f"death_7_two_id_{interaction.user.id}", label="2枚とる")
      death_three_button = discord.ui.Button(style=discord.ButtonStyle.primary, custom_id=f"death_7_three_id_{interaction.user.id}", label="3枚とる")
      death_result_button = discord.ui.Button(style=discord.ButtonStyle.success, custom_id=f"death_7_result_id_{interaction.user.id}", label="結果まで飛ばす")
      view.add_item(death_one_button)
      view.add_item(death_two_button)
      view.add_item(death_three_button)
      view.add_item(death_result_button)
      death_stage2_good_embed = discord.Embed(title=f"テーブルのコイン: {savedata[interaction.user.id][5]}枚", color=discord.Color.blue())
      savedata[interaction.user.id][0] = 7
      await interaction.channel.send(embed=death_stage2_good_embed, view=view)
  else:
      savedata[interaction.user.id][3] += (savedata[interaction.user.id][5]+3) % 4
      await interaction.channel.send(f"「ボクは{(savedata[interaction.user.id][5]+3) % 4}枚とるよ。」\n"
          "「この時点でボクが勝つことは確定しているけど、まだ続ける？」")
      savedata[interaction.user.id][5] -= (savedata[interaction.user.id][5]+3) % 4
      view = discord.ui.View()
      death_one_button = discord.ui.Button(style=discord.ButtonStyle.primary, custom_id=f"death_7_one_id_{interaction.user.id}", label="1枚とる")
      death_two_button = discord.ui.Button(style=discord.ButtonStyle.primary, custom_id=f"death_7_two_id_{interaction.user.id}", label="2枚とる")
      death_three_button = discord.ui.Button(style=discord.ButtonStyle.primary, custom_id=f"death_7_three_id_{interaction.user.id}", label="3枚とる")
      death_giveup_button = discord.ui.Button(style=discord.ButtonStyle.danger, custom_id=f"death_7_giveup_id_{interaction.user.id}", label="降参する")
      death_reset_button = discord.ui.Button(style=discord.ButtonStyle.danger, custom_id=f"reset_{interaction.user.id}", label="/reset")
      view.add_item(death_one_button)
      view.add_item(death_two_button)
      view.add_item(death_three_button)
      view.add_item(death_giveup_button)
      view.add_item(death_reset_button)
      death_stage2_bad_embed = discord.Embed(title=f"テーブルのコイン: {savedata[interaction.user.id][5]}枚", color=discord.Color.blue())
      savedata[interaction.user.id][0] = 7
      await interaction.channel.send(embed=death_stage2_bad_embed, view=view)


async def death_stage2_player(interaction, choice):
  if savedata[interaction.user.id][5] < choice:
      savedata[interaction.user.id][0] = 7
      await interaction.followup.send("「テーブルのコインが足りないよ。」", ephemeral=True)
  else:
      savedata[interaction.user.id][4] += choice
      savedata[interaction.user.id][5] -= choice
      await death_stage2_check(interaction)


async def death_stage2_result(interaction):
  await asyncio.sleep(0.3)
  await interaction.channel.send("「ボクが最後の1枚をとって、キミの勝ち！」")
  if savedata[interaction.user.id][1] == 0:
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
  if savedata[interaction.user.id][1] == 0:
      savedata[interaction.user.id][1] = 1
      await asyncio.sleep(0.3)
      await interaction.channel.send("「……拍子抜けしたでしょ？」")
      await asyncio.sleep(0.3)
      await interaction.channel.send("「借りたものを返すなんて、わざわざルールに書くまでもないよね。」")
      await asyncio.sleep(0.3)
      await interaction.channel.send("## 「だって当たり前のことだもんね！」")
      await interaction.channel.send(file=discord.File(R"illust\dekaibokudayo.png"))
  await asyncio.sleep(0.3)
  await interaction.channel.send(f"「それじゃあ、ステージ1でキミに貸した{savedata[interaction.user.id][6]}枚の{interaction.user.name}コイン、」")
  await asyncio.sleep(0.3)
  await interaction.channel.send("「耳をそろえて返してよ！」")
  await interaction.channel.send(file=discord.File(R"illust\misebirakashi.png"))
  death_stage3_return_embed = discord.Embed(title="返してくれる？", color=discord.Color.blue())
  death_stage3_return_button = discord.ui.Button(style=discord.ButtonStyle.primary, custom_id=f"death_8_id_{interaction.user.id}", label="はい")
  death_reset_button = discord.ui.Button(style=discord.ButtonStyle.danger, custom_id=f"reset_{interaction.user.id}", label="/reset")
  view = discord.ui.View()
  view.add_item(death_stage3_return_button)
  view.add_item(death_reset_button)
  await asyncio.sleep(0.3)
  savedata[interaction.user.id][0] = 8
  await interaction.channel.send(embed=death_stage3_return_embed, view=view)


async def death_stage2_giveup(interaction):
  await asyncio.sleep(0.3)
  await interaction.followup.send("「キミが最後の1枚をとったから、ボクの勝ち！」")
  await asyncio.sleep(0.3)
  await interaction.channel.send("「ステージ3には進めないよ。残念だったね。」")
  await asyncio.sleep(0.3)
  await interaction.channel.send("「まだやる気があるなら、/resetで最初からやり直す？」")
  death_reset_embed = discord.Embed(title="やり直す？", color=discord.Color.red())
  view = discord.ui.View()
  death_reset_button = discord.ui.Button(style=discord.ButtonStyle.danger, custom_id=f"reset_{interaction.user.id}", label="/reset")
  view.add_item(death_reset_button)
  savedata[interaction.user.id][0] = 9
  await interaction.channel.send(embed=death_reset_embed, view=view)


class MyModal(discord.ui.Modal, title='ステージ1'):
  borrow_input = discord.ui.TextInput(label='何枚借りる？',
                     placeholder='コインを借りる枚数を入力(数字のみ)',
                     required=True,
                     max_length=5)
  async def on_submit(self, interaction: discord.Interaction):
      borrowed_coin = int(self.borrow_input.value)
      if 0 <= borrowed_coin <= 65533:
          savedata[interaction.user.id][0] = 10
          savedata[interaction.user.id][4] = borrowed_coin + 1
          savedata[interaction.user.id][6] = borrowed_coin
          savedata[interaction.user.id][3] = 65533 - borrowed_coin
          death_ask_borrow_embed = discord.Embed(title=f"借りる枚数は、{savedata[interaction.user.id][6]}枚でいい？", color=discord.Color.blue())
          view = discord.ui.View()
          death_stage1_ok_button = discord.ui.Button(style=discord.ButtonStyle.primary, custom_id=f"death_3_go_id_{interaction.user.id}", label="はい")
          death_stage1_ng_button = discord.ui.Button(style=discord.ButtonStyle.primary, custom_id=f"death_3_re_id_{interaction.user.id}", label="訂正する")
          view.add_item(death_stage1_ok_button)
          view.add_item(death_stage1_ng_button)
          savedata[interaction.user.id][0] = 3
          await interaction.response.send_message(embed=death_ask_borrow_embed, view=view) 
      else:
          await interaction.response.send_message("「0から65533までの数字だけを入力してね。」", ephemeral=True)


# エイプリルフール用機能
@tree.command(name='game', description='Sokaikunとゲームができます。実行はDMやミュート推奨で。')
async def game(interaction: discord.Interaction):
  await interaction.response.send_message("オーケー！", ephemeral=True)
  death_embed = discord.Embed(title="ゲームを始める？", color=discord.Color.red())
  death_button = discord.ui.Button(style=discord.ButtonStyle.primary, custom_id="yattare_id", label="はい")
  view = discord.ui.View()
  view.add_item(death_button)
  await interaction.channel.send(embed=death_embed, view=view)


@tree.command(name='coin', description='手持ちコインの状況を確認します。')
async def coin(interaction: discord.Interaction):
  if savedata[interaction.user.id][0] >= 1:
      coin_message = f"手持ちコイン: {savedata[interaction.user.id][4]} (借りたコイン: {savedata[interaction.user.id][6]})\nSokaikunの手持ちコイン: {savedata[interaction.user.id][3]}"
      if savedata[interaction.user.id][1] == 2:
          if savedata[interaction.user.id][6] == 0 and savedata[interaction.user.id][4] > savedata[interaction.user.id][2]:
              await interaction.response.send_message("「ハイスコアを更新したよ！」")
              savedata[interaction.user.id][2] = savedata[interaction.user.id][4]
              await interaction.channel.send(coin_message.replace(" (借りたコイン: 0)", "") + f"\nクリア済☆\nHi Score: {savedata[interaction.user.id][2]}")
          else:
              await interaction.response.send_message(coin_message.replace(" (借りたコイン: 0)", "") + f"\nクリア済☆\nHi Score: {savedata[interaction.user.id][2]}")
      else:
          await interaction.response.send_message(coin_message.replace(" (借りたコイン: 0)", ""))
  else:
      await interaction.response.send_message("「/gameで始められるゲームで使うコマンドだよ！」", ephemeral=True)


@tree.command(name='reset', description='ゲーム進行度やコイン所持数などの状況をリセットしてルール説明までもどります。')
async def reset(interaction: discord.Interaction):
  if savedata[interaction.user.id][0] >= 1:
      await death_stage1_rule(interaction)
  else:
      await interaction.response.send_message("「/gameで始められるゲームで使うコマンドだよ！」", ephemeral=True)


@tree.command(name='shop', description='sokaiyaを呼び出します。')
async def shop(interaction: discord.Interaction):
  if savedata[interaction.user.id][1] == 2:
      await interaction.response.send_message("「いらっしゃい！」", ephemeral=True)
      shop_embed = discord.Embed(title="なにか買っていく？", description="代金は購入時にキミの手持ちコインから引かれるよ。もらった代金はSokaiya金庫に保管するからボクの手持ちコインが増えたりはしないよ。Sokaiyaの利用状況は/resetのたびにリセットされるから、安心してじゃんじゃん買っていってね！", color=discord.Color.red())
      shop_embed.add_field(name="①ハイスコアチャレンジのルール　0コイン", value="クリア後限定、ハイスコアチャレンジのルール説明をする。")
      shop_embed.add_field(name="②Sokaikunアルゴリズム解説書　0コイン", value="ステージ1でのボクの行動選択アルゴリズムが分かる。\n\n")
      shop_embed.add_field(name="③チートコード　20000コイン", value="購入した直後に使用される。キミとボクの手持ちコインを入れ替える。借りたコインの枚数は変化しない。")
      item_1_button = discord.ui.Button(style=discord.ButtonStyle.primary, custom_id=f"item_1_id_{interaction.user.id}", label="①を買う")
      item_2_button = discord.ui.Button(style=discord.ButtonStyle.primary, custom_id=f"item_2_id_{interaction.user.id}", label="②を買う")
      item_3_button = discord.ui.Button(style=discord.ButtonStyle.primary, custom_id=f"item_3_id_{interaction.user.id}", label="③を買う")
      view = discord.ui.View()
      view.add_item(item_1_button)
      view.add_item(item_2_button)
      view.add_item(item_3_button)
      await interaction.channel.send(embed=shop_embed, view=view)
  else:
      await interaction.response.send_message("「これはゲームクリア後のコマンドだよ！」", ephemeral=True)


TOKEN = os.getenv("DISCORD_TOKEN")
# Web サーバの立ち上げ
keep_alive()
client.run(TOKEN)
