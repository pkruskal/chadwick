#
# $Source$
# $Date$
# $Revision$
#
# DESCRIPTION:
# Dialog for selecting games to import
# 
# This file is part of Chadwick, a library for baseball play-by-play and stats
# Copyright (C) 2005, Ted Turocy (turocy@econ.tamu.edu)
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
#

from wxPython.wx import *
from wxPython.grid import *
from libchadwick import *

#
# This is virtually identical to the GameListCtrl in panelgamelist.
# TODO: Refactor into common base class
#
class GameListCtrl(wxListCtrl):
    def __init__(self, parent):
        wxListCtrl.__init__(self, parent, -1,
                            wxDefaultPosition, wxSize(550, 400),
                            style = wxLC_VIRTUAL | wxLC_REPORT)
        self.filter = lambda x: True

        self.InsertColumn(0, "Date")
        self.InsertColumn(1, "#")
        self.InsertColumn(2, "Visitors")
        self.InsertColumn(3, "Home")
        self.InsertColumn(4, "Win")
        self.InsertColumn(5, "Loss")
        self.InsertColumn(6, "Save")

        self.SetColumnWidth(0, 100)
        self.SetColumnWidth(1, 25)
        self.SetColumnWidth(2, 200)
        self.SetColumnWidth(3, 200)
        self.SetColumnWidth(4, 150)
        self.SetColumnWidth(5, 150)
        self.SetColumnWidth(6, 150)

        item = wxListItem()
        item.m_format = wxLIST_FORMAT_CENTRE
        item.m_mask = wxLIST_MASK_FORMAT
        for col in range(7):  self.SetColumn(col, item)

    def OnUpdate(self, book, f):
        """
        Update grid to list all games in scorebook 'book' matching
        filter function 'f'
        """
        self.book = book
        self.games = [ g for g in book.Games(f) ]
        self.SetItemCount(book.NumGames(f))

    def OnGetItemText(self, item, col):
        game = self.games[item]
        if col == 0:
            return game.GetDate()
        elif col == 1:
            return { 0: "", 1: "1", 2: "2" }[game.GetNumber()]
        elif col == 2:
            return (self.book.GetTeam(game.GetTeam(0)).GetName() + " " +
                    str(game.GetScore()[0]))
        elif col == 3:
            return (self.book.GetTeam(game.GetTeam(1)).GetName() + " " +
                    str(game.GetScore()[1]))
        elif col == 4:
            pitcher = game.GetWinningPitcher()
            if pitcher != "":
                return self.book.GetPlayer(pitcher).GetName()
            else:
                return ""
        elif col == 5:
            pitcher = game.GetLosingPitcher()
            if pitcher != "":
                return self.book.GetPlayer(pitcher).GetName()
            else:
                return ""
        else:
            pitcher = game.GetSavePitcher()
            if pitcher != "":
                return self.book.GetPlayer(pitcher).GetName()
            else:
                return ""

    def GetFilter(self):  return self.filter

    def GetSelectedGames(self):
        games = [ ]
        for index in range(len(self.games)):
            if self.GetItemState(index, wxLIST_STATE_SELECTED) == wxLIST_STATE_SELECTED:
                games.append(self.games[index])
        return games

class ImportDialog(wxDialog):
    def __init__(self, parent, book):
        wxDialog.__init__(self, parent, -1, "Select games to import")

        sizer = wxBoxSizer(wxVERTICAL)

        self.gameList = GameListCtrl(self)
        self.gameList.OnUpdate(book, lambda x: True)

        sizer.Add(self.gameList, 0, wxALL | wxEXPAND, 5)

        buttonSizer = wxBoxSizer(wxHORIZONTAL)
        buttonSizer.Add(wxButton(self, wxID_CANCEL, "Cancel"),
                                 0, wxALL | wxALIGN_CENTER, 5)
        buttonSizer.Add(wxButton(self, wxID_OK, "OK"), 0,
                        wxALL | wxALIGN_CENTER, 5)
        sizer.Add(buttonSizer, 0, wxALL | wxALIGN_RIGHT, 5)

        self.SetSizer(sizer)
        self.Layout()
        sizer.SetSizeHints(self)

    def GetSelectedGames(self):  return self.gameList.GetSelectedGames()
