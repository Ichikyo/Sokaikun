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

intents = discord.Intents.all()
client = discord.Client(intents=intents) 
tree = app_commands.CommandTree(client)


# 起動時
@client.event
async def on_ready():
    try:
        activity = f"テスト"
        await client.change_presence(activity=discord.Game(activity))
        await tree.sync()
        print("コマンドが正常に同期されました。")
    except Exception as e:
        print(f"コマンドの同期中にエラーが発生しました: {e}")


# テスト用コマンド
@tree.command(name="hello", description="Say hello to the world!") 
async def hello(interaction: discord.Interaction): 
  await interaction.response.send_message("Hello, World!")


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
              res = np.random.randint(1, splited[1])
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
    del_embed = discord.Embed(title="総会の委任はこちらから", color=discord.Color.green())
    del_button = discord.ui.Button(style=discord.ButtonStyle.primary, custom_id="del_id", label="委任/取消")
    view = discord.ui.View()
    view.add_item(del_button)
    await interaction.channel.send(embed=del_embed, view=view)


@tree.command(name="sokai_1", description="総会Step1 出席者更新&委任票集計 要管理者権限")
@discord.app_commands.guild_only()
@discord.app_commands.default_permissions(administrator=True)
async def sokai_1(interaction: Interaction):
  sokai_vc = discord.utils.get(interaction.guild.voice_channels, name = "総会")
  if sokai_vc.members == []:
      await interaction.response.send_message("エラー: ボイスチャンネル[総会]に誰もいません。", ephemeral=True)
      return
  del_role = discord.utils.get(interaction.guild.roles, name = "委任宣言者")
  if del_role == None:
      await interaction.response.send_message("エラー: ロール[委任宣言者]を見つけられませんでした。", ephemeral=True)
      return
  pre_role = discord.utils.get(interaction.guild.roles, name = "出席者")
  if pre_role:
      for i in pre_role.members:
          try:
              await i.remove_roles(discord.Object(int(pre_role.id)))
          except discord.Forbidden:
              await interaction.response.send_message("エラー: ロールを削除できません。権限が不足している可能性があります。", ephemeral=True)
              return
  else:
      await interaction.response.send_message("エラー: ロール[出席者]を見つけられませんでした。", ephemeral=True)
      return
  sokai_1_message = "総会\n### 出席者\n"
  del_member = del_role.members
  pre_member = sokai_vc.members
  del_number = [0]*len(pre_member)
  del_number_index = random.choices(range(len(pre_member)), k = len(del_member))
  print(del_number_index)
  for i in del_number_index:
      del_number[i] += 1
  sokai_1_message += "、".join([pre_member[i].display_name + f"(+{str(del_number[i])})" for i in range(len(pre_member))])
  await interaction.response.send_message(sokai_1_message.replace("(+0)", ""))
  for i in pre_member:
      try:
          await i.add_roles(pre_role)
      except discord.Forbidden:
          await interaction.response.send_message("エラー: ロールを付与できません。権限が不足している可能性があります。", ephemeral=True)
          return


@tree.command(name="sokai_2", description="総会Step2 委任者更新 要管理者権限")
@discord.app_commands.guild_only()
@discord.app_commands.default_permissions(administrator=True)
async def sokai_2(interaction: Interaction):
  del_role = discord.utils.get(interaction.guild.roles, name = "委任宣言者")
  if del_role == None:
      await interaction.response.send_message("エラー: ロール[委任宣言者]を見つけられませんでした。", ephemeral=True)
      return
  deled_role = discord.utils.get(interaction.guild.roles, name = "委任者")
  if deled_role:
      for i in deled_role.members:
          try:
              await i.remove_roles(discord.Object(int(deled_role.id)))
          except discord.Forbidden:
              await interaction.response.send_message("エラー: ロールを削除できません。権限が不足している可能性があります。", ephemeral=True)
              return
  for i in del_role.members:
      try:
          await i.add_roles(deled_role)
          await i.remove_roles(discord.Object(int(del_role.id)))
      except discord.Forbidden:
          await interaction.response.send_message("エラー: ロールを付与または削除できません。権限が不足している可能性があります。", ephemeral=True)
          return
  sokai_2_message = "### 委任者\n"
  sokai_2_message += "、".join(i.display_name for i in deled_role.members)
  await interaction.response.send_message(sokai_2_message)


@tree.command(name="sokai_all", description="総会Step1&2 要管理者権限")
@discord.app_commands.guild_only()
@discord.app_commands.default_permissions(administrator=True)
async def sokai_all(interaction: Interaction):
  sokai_vc = discord.utils.get(interaction.guild.voice_channels, name = "総会")
  if sokai_vc.members == []:
      await interaction.response.send_message("エラー: ボイスチャンネル[総会]に誰もいません。", ephemeral=True)
      return
  del_role = discord.utils.get(interaction.guild.roles, name = "委任宣言者")
  if del_role == None:
      await interaction.response.send_message("エラー: ロール[委任宣言者]を見つけられませんでした。", ephemeral=True)
      return
  pre_role = discord.utils.get(interaction.guild.roles, name = "出席者")
  if pre_role:
      for i in pre_role.members:
          try:
              await i.remove_roles(discord.Object(int(pre_role.id)))
          except discord.Forbidden:
              await interaction.response.send_message("エラー: ロールを削除できません。権限が不足している可能性があります。", ephemeral=True)
              return
  else:
      await interaction.response.send_message("エラー: ロール[出席者]を見つけられませんでした。", ephemeral=True)
      return
  deled_role = discord.utils.get(interaction.guild.roles, name = "委任者")
  if deled_role:
      for i in deled_role.members:
          try:
              await i.remove_roles(discord.Object(int(deled_role.id)))
          except discord.Forbidden:
              await interaction.response.send_message("エラー: ロールを削除できません。権限が不足している可能性があります。", ephemeral=True)
              return
  sokai_all_message = "総会\n### 出席者\n"
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
          await interaction.response.send_message("エラー: ロールを付与できません。権限が不足している可能性があります。", ephemeral=True)
          return
  for i in del_role.members:
      try:
          await i.add_roles(deled_role)
          await i.remove_roles(discord.Object(int(del_role.id)))
      except discord.Forbidden:
          await interaction.response.send_message("エラー: ロールを付与または削除できません。権限が不足している可能性があります。", ephemeral=True)
          return
  sokai_all_message += "\n### 委任者\n"
  sokai_all_message += "、".join(i.display_name for i in deled_role.members)
  await interaction.response.send_message(sokai_all_message.replace("(+0)", ""))


# ロールパネル
role_panel_message = None
@tree.command(name='rolepanel', description='ロールパネルを作成します')
@app_commands.describe(description='ロールパネルの説明',)
@discord.app_commands.guild_only()
@discord.app_commands.default_permissions(administrator=True)
async def rolepanel(interaction: Interaction,ロール1: discord.Role,ロール2: Optional[discord.Role] = None,ロール3: Optional[discord.Role] = None,ロール4: Optional[discord.Role] = None,ロール5: Optional[discord.Role] = None,ロール6: Optional[discord.Role] = None,ロール7: Optional[discord.Role] = None,ロール8: Optional[discord.Role] = None,ロール9: Optional[discord.Role] = None,ロール10: Optional[discord.Role] = None,ロール11: Optional[discord.Role] = None,ロール12: Optional[discord.Role] = None,ロール13: Optional[discord.Role] = None,ロール14: Optional[discord.Role] = None,ロール15: Optional[discord.Role] = None,ロール16: Optional[discord.Role] = None,ロール17: Optional[discord.Role] = None,ロール18: Optional[discord.Role] = None,ロール19: Optional[discord.Role] = None,ロール20: Optional[discord.Role] = None,ロール21: Optional[discord.Role] = None,ロール22: Optional[discord.Role] = None,ロール23: Optional[discord.Role] = None,ロール24: Optional[discord.Role] = None,description:str=''):
    global role_panel_message
    warning_embed = discord.Embed(
        description="パネルを作成しました！",
        color=discord.Color.green(),
    )
    await interaction.response.send_message(embed=warning_embed, ephemeral=True)
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
