/**
 * Language Switcher Component
 *
 * Provides a dropdown menu for users to switch between supported languages.
 * Persists language preference to localStorage.
 */

import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  IconButton,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Tooltip,
  Typography,
  Box,
} from '@mui/material';
import LanguageIcon from '@mui/icons-material/Language';
import CheckIcon from '@mui/icons-material/Check';

import { supportedLanguages, type SupportedLanguage } from '../../../i18n';

interface LanguageSwitcherProps {
  /** Show full language names instead of flags */
  showLabels?: boolean;
  /** Size of the icon button */
  size?: 'small' | 'medium' | 'large';
  /** Custom icon color */
  color?: 'inherit' | 'default' | 'primary' | 'secondary';
}

export const LanguageSwitcher: React.FC<LanguageSwitcherProps> = ({
  showLabels = false,
  size = 'medium',
  color = 'inherit',
}) => {
  const { i18n, t } = useTranslation('settings');
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const open = Boolean(anchorEl);

  const handleClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleLanguageChange = (languageCode: SupportedLanguage) => {
    i18n.changeLanguage(languageCode);
    handleClose();
  };

  const currentLanguage = supportedLanguages.find(
    (lang) => lang.code === i18n.language
  ) || supportedLanguages[0];

  return (
    <>
      <Tooltip title={t('language.title', 'Language')}>
        <IconButton
          onClick={handleClick}
          size={size}
          color={color}
          aria-label="change language"
          aria-controls={open ? 'language-menu' : undefined}
          aria-haspopup="true"
          aria-expanded={open ? 'true' : undefined}
        >
          {showLabels ? (
            <Box display="flex" alignItems="center" gap={0.5}>
              <Typography variant="body2">{currentLanguage.flag}</Typography>
              <Typography variant="body2">{currentLanguage.code.toUpperCase()}</Typography>
            </Box>
          ) : (
            <LanguageIcon />
          )}
        </IconButton>
      </Tooltip>

      <Menu
        id="language-menu"
        anchorEl={anchorEl}
        open={open}
        onClose={handleClose}
        MenuListProps={{
          'aria-labelledby': 'language-button',
        }}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'right',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
      >
        {supportedLanguages.map((language) => (
          <MenuItem
            key={language.code}
            onClick={() => handleLanguageChange(language.code)}
            selected={i18n.language === language.code}
          >
            <ListItemIcon>
              <Typography variant="body1">{language.flag}</Typography>
            </ListItemIcon>
            <ListItemText
              primary={language.nativeName}
              secondary={language.name !== language.nativeName ? language.name : undefined}
            />
            {i18n.language === language.code && (
              <CheckIcon fontSize="small" color="primary" sx={{ ml: 1 }} />
            )}
          </MenuItem>
        ))}
      </Menu>
    </>
  );
};

export default LanguageSwitcher;
