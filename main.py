import discord
from discord.ext import commands
from discord import app_commands
from discord import Interaction
from typing import Optional
import random
import re
import numpy as np
import os
from keep_alive import keep_alive
import json
import asyncio


intents = discord.Intents.all()
client = discord.Client(intents=intents) 
tree = app_commands.CommandTree(client)


# 起動時
@client.event
async def on_ready():
    try:
        await tree.sync()
        print("コマンドが正常に同期されました。")
    except Exception as e:
        print(f"コマンドの同期中にエラーが発生しました: {e}")
    while True:
        await change_activity()


async def change_activity():
    activity = random.choice(
        [":flag_bt:"])
    await client.change_presence(activity=discord.Game(activity))
    await asyncio.sleep(10000)


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
      "GitHubにアップロードしたソースコードをRenderとUptimeRobotによって常時起動しているため、"
      "それらのサイトやDiscord自体の変更によって機能停止する場合があることをご了承ください。\n"
      "サーバーでのコマンド実行が主な機能ですが、一部のコマンドはSokaikunへのDMでも実行可能です。\n"
      "## 必要なセットアップ\n"
      "Sokaikunに管理者権限を与えてサーバーに招待したら、それぞれロール名が 参加者 , 委任者 , 委任宣言者 である3つのロールを作成し、"
      "Sokaikunのロールをそれらより上位に設定してください。"
      "また、総会を行うボイスチャンネルの名前は 総会 としておいてください。\n"
      "__**※注意 このとき絶対にSokaikunを管理者などの重要なロールより上位にしてはいけません。"
      "Sokaikunより下位のロールは/rolepanelによりだれでも（明示的にですが）取得可能になります。**__\n"
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
      "- **/rolepanel**\n"
      "ボタンを押すことでロールの付与・剥奪が可能なパネルを作成します。"
      "引数にロールを入れることで対応するボタンが増えます。"
      "ボタンを押すと自身にロールが付与され、既に付与されていた場合は剥奪されます。"
      "最後の引数のdescriptionはパネルに表示される説明文です。\n"
      "- **/del** [管理者のみ実行可能]\n"
      "委任宣言を行うボタンを作成します。"
      "**/rolepanel**の仕組みを応用して、[委任宣言者]という名前のロールに対応するボタンが作成されます。"
      "次回総会を委任予定の人は押してください。委任票は参加者へランダムに振り分けられます。"
      "但し、特定の人物に票を委任したい場合はボタンを押さずに一般チャンネルへ書き込んでください。\n"
      "- **/sokai_1** [管理者のみ実行可能]\n"
      "ボイスチャンネル 総会 に接続しているメンバーを取得し、参加者一覧として表示します。"
      "また、その時点での委任宣言者ロールの保有者数を委任票として、参加者へランダムに振り分けます。"
      "獲得した委任票の数は参加者一覧の名前横に (+◯) の形で表示され、その数が余分に獲得した投票数となります。"
      "獲得した委任票が0票の場合は名前横に何も表示されません。"
      "このコマンドを実行後、 [参加者ロール保有者] = [ボイスチャンネル総会に接続していたメンバー] となります。\n"
      "- **/sokai_2** [管理者のみ実行可能]\n"
      "委任宣言者ロール保有者を取得し、委任者一覧として表示します。"
      "このコマンドを実行後、 [委任者ロール保有者] = [元委任宣言者ロール保有者] , [委任宣言者ロール保有者] = [なし] となります。\n"
      "**/sokai_1**および**/sokai_2**は、特定の人物への名指し委任があった場合を想定して分離されています。"
      "**/sokai_1**を実行後、名指しで委任を行った委任者に手動で委任宣言者ロールを付与し、**/sokai_2**を実行してください。"
      "名指しの委任は参加者一覧に計上できないため、各自で確認する必要があります。\n"
      "- **/sokai_all** [管理者のみ実行可能]\n"
      "**/sokai_1**と**/sokai_2**をつなげて使用できるコマンドです。"
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
    global del_message
    warning_embed = discord.Embed(
        description="委任を開始しました！",
        color=discord.Color.green(),
    )
    await interaction.response.send_message(embed=warning_embed)
    del_embed = discord.Embed(title="総会の委任はこちらから", description="特定の人物に委任したい場合は、ボタンを押さずに一般チャンネルへその旨を記載してください", color=discord.Color.green())
    del_button = discord.ui.Button(style=discord.ButtonStyle.primary, custom_id="del_id", label="委任/取消")
    view = discord.ui.View()
    view.add_item(del_button)
    await interaction.channel.send(embed=del_embed, view=view)


@tree.command(name="sokai_1", description="総会Step1 参加者更新&委任票集計 要管理者権限")
@discord.app_commands.guild_only()
@discord.app_commands.default_permissions(administrator=True)
async def sokai_1(interaction: Interaction):
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
              await i.remove_roles(pre_role)
          except discord.Forbidden:
              await interaction.followup.send("エラー: ロールを削除できません。権限が不足している可能性があります。", ephemeral=True)
              return
  else:
      await interaction.followup.send("エラー: ロール[参加者]を見つけられませんでした。", ephemeral=True)
      return
  sokai_1_message = "総会\n### 参加者\n"
  del_member = del_role.members
  pre_member = sokai_vc.members
  del_number = [0]*len(pre_member)
  del_number_index = random.choices(range(len(pre_member)), k = len(del_member))
  for i in del_number_index:
      del_number[i] += 1
  sokai_1_message += "、".join([pre_member[i].display_name + f"(+{str(del_number[i])})" for i in range(len(pre_member))])
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
  sokai_2_message = "### 委任者\n"
  sokai_2_message += "、".join(i.display_name for i in new_deled_role.members)
  await interaction.followup.send(sokai_2_message)


@tree.command(name="sokai_all", description="総会Step1&2 要管理者権限")
@discord.app_commands.guild_only()
@discord.app_commands.default_permissions(administrator=True)
async def sokai_all(interaction: Interaction):
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
  sokai_all_message = "総会\n### 参加者\n"
  del_member = del_role.members
  pre_member = sokai_vc.members
  del_number = [0]*len(pre_member)
  del_number_index = random.choices((range(len(pre_member))), k = len(del_member))
  for i in del_number_index:
      del_number[i] += 1
  sokai_all_message += "、".join([pre_member[i].display_name + f"(+{str(del_number[i])})" for i in range(len(pre_member))])
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
  sokai_all_message += "\n### 委任者\n"
  sokai_all_message += "、".join(i.display_name for i in new_deled_role.members)
  await interaction.followup.send(sokai_all_message.replace("(+0)", ""))



# ロールパネル
role_panel_message = None
@tree.command(name='rolepanel', description='ロールパネルを作成します')
@app_commands.describe(description='ロールパネルの説明',)
@discord.app_commands.guild_only()
async def rolepanel(interaction: Interaction,ロール1: discord.Role,ロール2: Optional[discord.Role] = None,ロール3: Optional[discord.Role] = None,ロール4: Optional[discord.Role] = None,ロール5: Optional[discord.Role] = None,ロール6: Optional[discord.Role] = None,ロール7: Optional[discord.Role] = None,ロール8: Optional[discord.Role] = None,ロール9: Optional[discord.Role] = None,ロール10: Optional[discord.Role] = None,ロール11: Optional[discord.Role] = None,ロール12: Optional[discord.Role] = None,ロール13: Optional[discord.Role] = None,ロール14: Optional[discord.Role] = None,ロール15: Optional[discord.Role] = None,ロール16: Optional[discord.Role] = None,ロール17: Optional[discord.Role] = None,ロール18: Optional[discord.Role] = None,ロール19: Optional[discord.Role] = None,ロール20: Optional[discord.Role] = None,ロール21: Optional[discord.Role] = None,ロール22: Optional[discord.Role] = None,ロール23: Optional[discord.Role] = None,ロール24: Optional[discord.Role] = None,description:str=''):
    global role_panel_message
    warning_embed = discord.Embed(
        description="パネルを作成しました！",
        color=discord.Color.green(),
    )
    await interaction.response.send_message(embed=warning_embed)
    panel_embed = discord.Embed(title='ロールパネル', color=discord.Color.green())
    buttons = []
    role_data = []
    roles = [
        ロール1, ロール2, ロール3, ロール4, ロール5,
        ロール6, ロール7, ロール8, ロール9, ロール10,
        ロール11, ロール12, ロール13, ロール14, ロール15,
        ロール16, ロール17, ロール18, ロール19, ロール20,
        ロール21, ロール22, ロール23, ロール24,
    ]
    view = discord.ui.View()
    left_description_text = ""
    left_value_text = ""
    right_description_text = ""
    right_value_text = ""
    for i, role in enumerate(roles):
        if role:
            custom_id = f"rolepanel{i + 1}"
            button = discord.ui.Button(style=discord.ButtonStyle.primary, custom_id=custom_id, label=str(i+1))
            buttons.append(button)
            view.add_item(button)
            role_data.append({"rolenumber": i + 1, "rolename": role.name, "roleid": str(role.id)})
            if i < 12:
                left_description_text += f"{i + 1}: {role.mention}\n"
                left_value_text += f"{i + 1}: {role.mention}\n"
            else:
                right_description_text += f"{i + 1}: {role.mention}\n"
                right_value_text += f"{i + 1}: {role.mention}\n"
    panel_embed.add_field(name='', value=description, inline=False)
    panel_embed.add_field(name='', value=left_value_text, inline=True)
    panel_embed.add_field(name='', value=right_value_text, inline=True)
    role_panel_message = await interaction.channel.send(embed=panel_embed, view=view)
    directory_path = f'data/{interaction.guild.id}/{interaction.channel.id}/rolepanel/'
    os.makedirs(directory_path, exist_ok=True)
    role_panel_message_id = role_panel_message.id
    role_data.append({"message_id": role_panel_message_id})
    file_path = f'{directory_path}{role_panel_message_id}.json'
    with open(file_path, 'w', encoding='utf-8') as json_file:
        json.dump(role_data, json_file, ensure_ascii=False, indent=4)
    print(f"ロールパネルのメッセージID: {role_panel_message_id}")

@client.event
async def on_interaction(inter:discord.Interaction):
    try:
        if inter.data['component_type'] == 2:
            await on_button_click(inter)
    except KeyError:
        pass


async def on_button_click(interaction: discord.Interaction):
  custom_id = interaction.data["custom_id"]
  member = interaction.guild.get_member(interaction.user.id)
  if custom_id == "del_id":
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
              try:
                  await member.add_roles(del_role)
                  await interaction.response.send_message(f"ロールを付与しました: {del_role.name}", ephemeral=True)
              except discord.Forbidden:
                  await interaction.response.send_message("エラー: ロールを付与できません。権限が不足している可能性があります。", ephemeral=True)
          else:
              await interaction.response.send_message("エラー: ロール[委任宣言者]を見つけられませんでした。", ephemeral=True)
  elif custom_id.startswith("rolepanel"):
      role_number = int(custom_id.replace("rolepanel", ""))
      try:
          role_panel_message = await interaction.channel.fetch_message(interaction.message.id)
      except discord.HTTPException as e:
          print(f"Error fetching message: {e}")
          await interaction.response.send_message("エラー: メッセージを取得できませんでした。", ephemeral=True)
          return
      file_path = f'data/{interaction.guild.id}/{interaction.channel.id}/rolepanel/{interaction.message.id}.json'
      try:
          with open(file_path, 'r', encoding='utf-8') as json_file:
              role_data = json.load(json_file)
      except FileNotFoundError:
          print(f"File not found: {file_path}")
          await interaction.response.send_message("対応するファイルが見つかりませんでした。", ephemeral=True)
          return
      selected_role = next((role for role in role_data if role.get("rolenumber") == role_number), None)
      if selected_role:
          if discord.utils.get(member.roles, id=int(selected_role["roleid"])):
              try:
                  await member.remove_roles(discord.Object(int(selected_role["roleid"])))
                  await interaction.response.send_message(f"ロールを削除しました: {selected_role['rolename']}", ephemeral=True)
              except discord.Forbidden:
                  await interaction.response.send_message("エラー: ロールを削除できません。権限が不足している可能性があります。", ephemeral=True)
          else:
              role = interaction.guild.get_role(int(selected_role["roleid"]))
              if role:
                  try:
                      await member.add_roles(role)
                      await interaction.response.send_message(f"ロールを付与しました: {selected_role['rolename']}", ephemeral=True)
                  except discord.Forbidden:
                      await interaction.response.send_message("エラー: ロールを付与できません。権限が不足している可能性があります。", ephemeral=True)
              else:
                  await interaction.response.send_message("エラー: ロールを見つけられませんでした。", ephemeral=True)
      else:
          await interaction.response.send_message(f"エラー: ロール番号 {role_number} が見つかりませんでした。", ephemeral=True)


TOKEN = os.getenv("DISCORD_TOKEN")
# Web サーバの立ち上げ
keep_alive()
client.run(TOKEN)
