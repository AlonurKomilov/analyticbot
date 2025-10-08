import React, { useState } from 'react';
import {
    IconButton,
    Menu,
    MenuItem,
    Typography,
    Divider,
    Tooltip
} from '@mui/material';
import {
    Settings as SettingsIcon
} from '@mui/icons-material';
import { DENSITY_OPTIONS } from '../utils/tableUtils';

/**
 * TableDensity Component
 * Renders table density (padding) selection menu
 */
const TableDensity = ({
    density,
    setDensity
}) => {
    const [densityMenuAnchor, setDensityMenuAnchor] = useState(null);

    const handleDensityChange = (densityKey) => {
        setDensity(densityKey);
        setDensityMenuAnchor(null);
    };

    return (
        <>
            <Tooltip title="Table Density">
                <IconButton
                    onClick={(e) => setDensityMenuAnchor(e.currentTarget)}
                    aria-label="Change table density"
                >
                    <SettingsIcon />
                </IconButton>
            </Tooltip>

            <Menu
                anchorEl={densityMenuAnchor}
                open={Boolean(densityMenuAnchor)}
                onClose={() => setDensityMenuAnchor(null)}
            >
                <MenuItem disabled>
                    <Typography variant="subtitle2">Table Density</Typography>
                </MenuItem>
                <Divider />
                {DENSITY_OPTIONS.map(option => (
                    <MenuItem
                        key={option.key}
                        selected={density === option.key}
                        onClick={() => handleDensityChange(option.key)}
                    >
                        {option.label}
                    </MenuItem>
                ))}
            </Menu>
        </>
    );
};

export default TableDensity;
