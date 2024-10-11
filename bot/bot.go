package bot

import (
	"github.com/bwmarrin/discordgo"
)

// Session is the global Discord session
var Session *discordgo.Session

// NewBotSession creates a new Discord session
func NewBotSession(token string) (*discordgo.Session, error) {
	dg, err := discordgo.New("Bot " + token)
	if err != nil {
		return nil, err
	}
	return dg, nil
}

// RegisterHandlers registers event handlers for the bot
func RegisterHandlers() {
	Session.AddHandler(messageCreate)
	Session.AddHandler(messageReactionAdd)

	Session.Identify.Intents = discordgo.IntentsGuildMessages | discordgo.IntentsDirectMessages | discordgo.IntentsGuildMessageReactions

	err := Session.Open()
	if err != nil {
		panic("Cannot open the session: " + err.Error())
	}
}
