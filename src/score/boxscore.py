#
# $Source$
# $Date$
# $Revision$
#
# DESCRIPTION:
# A class to generate and store a boxscore for a game
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

from libchadwick import *

class Boxscore:
    def __init__(self, game):
        self.game = game

    def FindStats(self, id):
        for x in self.stats:
            for y in x:
                for z in y:
                    if z["id"] == id:  return z
                    
        return None
        
    def FindPitcher(self, id):
        for x in self.pitching:
            for y in x:
                if y["id"] == id:  return y
        return None

    def NewBattingStats(self, player):
        return { "id": player.player_id, "name": player.name,
                 "pos": [ player.pos ],
                 "ab":0, "r":0, "h":0,
                 "2b":0, "3b":0, "hr":0, "bi":0,
                 "bb":0, "ibb":0, "so":0,
                 "gdp":0, "hp":0, "sh":0, "sf":0,
                 "sb":0, "cs":0 }
                 
    def NewPitchingStats(self, player):
        return { "id": player.player_id, "name": player.name,
                 "outs":0, "r":0, "er":0, "h":0, "hr":0,
                 "bb":0, "ibb":0, "so":0,
                 "wp":0, "bk":0, "hb":0 }

    def AddSubs(self, gameiter):
        s = gameiter.event.first_sub

        while s != None:
            if self.FindStats(s.player_id) == None:
                # We don't have entries (for now) for pitchers who don't bat
                # because of the DH
                if s.slot > 0:
                    self.stats[s.team][s.slot-1].append(self.NewBattingStats(s))
            else:
                self.FindStats(s.player_id)["pos"].append(s.pos)
            
            if s.pos == 1:
                self.pitching[s.team].append(self.NewPitchingStats(s))
            s = s.next

    def Build(self):
        # TODO: It would be nice to be able to build this incrementally when
        # the game changes.
        self.stats = [ [], [] ]
        self.pitching = [ [], [] ]
        self.byInnings = [ [], [] ]
        for t in [0, 1]:
            starters = [ cw_game_starter_find(self.game, t, slot) for slot in xrange(1, 10) ]
            self.stats[t] = [ [ self.NewBattingStats(x) ] for x in starters ]

            pitcher = cw_game_starter_find_by_position(self.game, t, 1)
            self.pitching[t] = [ self.NewPitchingStats(pitcher) ]
        
        # Number of double plays turned by teams
        self.dp = [ 0, 0 ]
        self.win = ""
        self.loss = ""
        self.save = ""
        
        self.Tabulate(self.game)
        
            
    def Tabulate(self, game):
        gameiter = cw_gameiter_create(game)

        while gameiter.event != None:
            if gameiter.event.event_text == "NP":
                self.AddSubs(gameiter)
                cw_gameiter_next(gameiter)
                continue
            
            team = cw_gameiter_get_halfinning(gameiter)
            batterId = cw_gameiter_get_player(gameiter, team,
                                              cw_gameiter_num_batters(gameiter, team) % 9 + 1)

            batter = self.FindStats(batterId)
            pitcher = self.pitching[1-team][-1]
            event_data = gameiter.event_data
            
            if cw_event_is_official_ab(event_data):
                batter["ab"] += 1
            pitcher["outs"] += cw_event_outs_on_play(event_data)

            if event_data.event_type == CW_EVENT_SINGLE:
                batter["h"] += 1
                pitcher["h"] += 1
            elif event_data.event_type == CW_EVENT_DOUBLE:
                batter["h"] += 1
                pitcher["h"] += 1
                batter["2b"] += 1
            elif event_data.event_type == CW_EVENT_TRIPLE:
                batter["h"] += 1
                pitcher["h"] += 1
                batter["3b"] += 1
            elif event_data.event_type == CW_EVENT_HOMERUN:
                batter["h"] += 1
                pitcher["h"] += 1
                batter["hr"] += 1
                pitcher["hr"] += 1
            elif event_data.event_type == CW_EVENT_WALK:
                batter["bb"] += 1
                pitcher["bb"] += 1
            elif event_data.event_type == CW_EVENT_INTENTIONALWALK:
                batter["bb"] += 1
                pitcher["bb"] += 1
                batter["ibb"] += 1
                pitcher["ibb"] += 1
            elif event_data.event_type == CW_EVENT_STRIKEOUT:
                batter["so"] += 1
                pitcher["so"] += 1
            elif event_data.event_type == CW_EVENT_HITBYPITCH:
                batter["hp"] += 1
                pitcher["hb"] += 1
            elif event_data.event_type == CW_EVENT_BALK:
                pitcher["bk"] += 1

            batter["bi"] += cw_event_rbi_on_play(event_data)

            if event_data.sh_flag > 0:
                batter["sh"] += 1
            if event_data.sf_flag > 0:
                batter["sf"] += 1
            if event_data.gdp_flag > 0:
                batter["gdp"] += 1
            if event_data.wp_flag > 0:
                pitcher["wp"] += 1

            if event_data.dp_flag > 0:
                self.dp[1-team] += 1

            inning = gameiter.event.inning
            halfInning = gameiter.event.half_inning

            if inning > len(self.byInnings[halfInning]):
                self.byInnings[halfInning].append(0)
                
            for base in [1,2,3]:
                if cw_gameiter_get_runner(gameiter, base) == "":
                    continue
                
                runner = self.FindStats(cw_gameiter_get_runner(gameiter, base))

                if cw_gameiter_get_advancement(gameiter, base) >= 4:
                    self.byInnings[halfInning][inning-1] += 1
                    runner["r"] += 1
                    resppitcher = self.FindPitcher(cw_gameiter_get_resp_pitcher(gameiter, base))
                    resppitcher["r"] += 1
                    if cw_gameiter_get_advancement(gameiter, base) != 5:
                        resppitcher["er"] += 1

                if cw_gameiter_get_sb_flag(gameiter, base) > 0:
                    runner["sb"] += 1
                if cw_gameiter_get_cs_flag(gameiter, base) > 0:
                    runner["cs"] += 1

            if cw_gameiter_get_advancement(gameiter, 0) >= 4:
                self.byInnings[halfInning][inning-1] += 1
                batter["r"] += 1
                pitcher["r"] += 1
                if cw_gameiter_get_advancement(gameiter, 0) != 5:
                    pitcher["er"] += 1

            cw_gameiter_next(gameiter)

        cw_gameiter_cleanup(gameiter)
        
    def GetDPs(self, team):   return self.dp[team]

