#!/usr/bin/env python
# -*- coding: latin-1 -*-
# Versão 1.3 - Betha
# CapturaSenhaChrome.py

# The MIT License (MIT)
#
# Copyright (c) 2014 - Ricardo Mantovani - Desenvolvimento Aberto
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# importa modulos
import wx
import wx.grid
import win32crypt
import sqlite3
import os
import getpass
import datetime
import platform

# Cria classe generica de uma WX.Grid
# A classe abaixo faz parte da documentação WXPython oficial
# Este trecho de código é util para manipular a grade


class GenericTable(wx.grid.PyGridTableBase):
    def __init__(self, data, rowLabels = None, colLabels = None):
        wx.grid.PyGridTableBase.__init__(self)
        self.data = data
        self.rowLabels = rowLabels
        self.colLabels = colLabels

    def GetNumberRows(self):
        return len(self.data)

    def GetNumberCols(self):
        return len(self.data[0])

    def GetColLabelValue(self, col):
        if self.colLabels:
            return self.colLabels[col]

    def GetRowLabelValue(self, row):
        if self.rowLabels:
            return self.rowLabels[row]

    def IsEmptyCell(self, row, col):
        return False

    def GetValue(self, row, col):
        return self.data[row][col]

    def SetValue(self, row, col, value):
        pass

# Inicializa Grade
dados = []
colLabels = ["Site (Action URL)", "Usuário (User)", "Senha (Password)"]
rowLabels = []
for linha in range(1, 150):
    rowLabels.append(str(linha))

# Conecta ao banco de dados do usuario local
# Requer elevação de privilegios se o Chrome estiver aberto
conn = sqlite3.connect(os.getenv("APPDATA") + "\..\Local\Google\Chrome\User Data\Default\Login Data")
cursor = conn.cursor()

# Captura informações de login
cursor.execute('SELECT action_url, username_value, password_value FROM logins')

# Retorna resultados
resultado = cursor.fetchall()
for result in resultado:
  # Descriptografa senha
  # CryptUnprotectData requer o contexto do usuario local
  senha = win32crypt.CryptUnprotectData(result[2], None, None, None, 0)[1]
  if senha:
      captura = [result[0], result[1], senha]
      dados.append(captura)

# Cria classe da grid
class SimpleGrid(wx.grid.Grid):
    def __init__(self, parent):
        wx.grid.Grid.__init__(self, parent, -1, pos=(5, 10), size=(850, 240))
        tableBase = GenericTable(dados, rowLabels, colLabels)
        self.SetTable(tableBase)

# Cria formulario


class Formulario(wx.Frame):
    def __init__(self, parent):
        # Cria Formulario
        wx.Frame.__init__(self, parent, -1, "DA - Google Chrome Password Recovery - Desenvolvimento Aberto - 2014", size=(880, 350))
        panel = wx.Panel(self, wx.ID_ANY)

        # Cria Menu
        menu = wx.Menu()
        menu.Append(5000, "S&alvar", "Exportar para texto")
        menu.Append(5001, "Sai&r", "Fechar o programa")

        menu1 = wx.Menu()
        menu1.Append(6001, "&Sobre", "Sobre este programa")

        # Cria Barra de menus
        menubarra = wx.MenuBar()
        menubarra.Append(menu, "&Arquivo")
        menubarra.Append(menu1, "&Sobre")
        self.SetMenuBar(menubarra)

        # Barra de status
        statusbar = self.CreateStatusBar(5)

        # Retorna data
        dataA = datetime.datetime.today()
        dataA = dataA.strftime('%d-%b-%Y')

        # Preenche barra de status
        self.SetStatusText("", 0)
        self.SetStatusText("Estação: " + os.environ['COMPUTERNAME'], 1)
        self.SetStatusText("Usuario: " + getpass.getuser(), 2)
        self.SetStatusText("Data Atual: " + dataA, 3)
        self.SetStatusText(self.plataforma(), 4)

        # Declara Eventos dos menus
        self.Bind(wx.EVT_MENU, self.OnSalvar, id=5000)
        self.Bind(wx.EVT_MENU, self.OnSair, id=5001)
        self.Bind(wx.EVT_MENU, self.OnSobre, id=6001)

        # Cria Grid de dados
        grid = SimpleGrid(panel)
        grid.SetColSize(0, 430)
        grid.SetColSize(1, 230)
        grid.SetColSize(2, 108)

    def plataforma(self):
        sistema = "OS: " + platform.system() + \
                  " - " + platform.release() + \
                  " - " + platform.version()
        return sistema

    # Cria evento para Salvar Arquivo.
    def OnSalvar(self, evt):
        saveFileDialog = wx.FileDialog(self, "Salvar Como", "", "",
                                       "Arquivos Texto (*.txt)|*.txt",
                                       wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)

        if saveFileDialog.ShowModal() == wx.ID_CANCEL: return

        # Cria arquivo e adiciona conteudo
        arquivo = saveFileDialog.GetPath()

        file = open(arquivo, "w")

        conteudo = "Google Chrome Password Recovery - Powered by Desenvolvimento Aberto 2014\n\n" + \
                   "Sistema Operacional: " + self.plataforma().replace("OS:","") + "\n" + \
                   "Estação: " + os.environ['COMPUTERNAME'] + "\n" + \
                   "Usuario: " + getpass.getuser() + "\n" + \
                   "Data Extração: " + datetime.datetime.today().strftime('%d-%b-%Y') + "\n\n" + \
                   "Registros encontrados: \n\n"

        for reg in dados:
            conteudo = conteudo + str(reg) + "\n"
        file.write(str(conteudo))
        file.close()
        saveFileDialog.Destroy()

    # Cria evento de saida
    def OnSair(self, evt):
        self.Close(True)

    # Cria evento sobre
    def OnSobre(self, evt):
        # Cria texto para ferramenta
        texto = "Powered by Desenvolvimento Aberto\n\n" + \
                "Autor: Ricardo Mantovani\n" + \
                "E-mail: desenvolvimento.aberto@live.com\n" + \
                "Versão: 1.1 - Betha\n\n" + \
                "Coogle Code:\n" + \
                "http://code.google.com/p/google-chome-pass-recovery"
        # Cria caixa de texto
        msg = wx.MessageBox(texto, 'Info', wx.OK | wx.ICON_INFORMATION)
        msg.ShowModal()

# Inicializa a aplicação
app = wx.App()
frame = Formulario(None)
frame.Show(True)
app.MainLoop()




