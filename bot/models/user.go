package models

import (
    "time"

    "gorm.io/gorm"
)

type User struct {
    ID        uint           `gorm:"primaryKey"`
    DiscordID string         `gorm:"uniqueIndex;not null"`
    Settings  UserSettings   `gorm:"constraint:OnUpdate:CASCADE,OnDelete:SET NULL;"`
    CreatedAt time.Time
    UpdatedAt time.Time
}

type UserSettings struct {
    ID            uint   `gorm:"primaryKey"`
    Theme         string `gorm:"default:'light'"`
    Notifications bool   `gorm:"default:true"`
    UserID        uint
    CreatedAt     time.Time
    UpdatedAt     time.Time
}
