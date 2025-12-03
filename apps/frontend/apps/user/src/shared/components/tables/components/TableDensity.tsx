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

interface TableDensityProps {
    density: string;
    setDensity: (density: string) => void;
}

/**
 * TableDensity Component
 * Renders table density (padding) selection menu
 */
const TableDensity: React.FC<TableDensityProps> = ({
    density,
    setDensity
}) => {
    const [densityMenuAnchor, setDensityMenuAnchor] = useState<null | HTMLElement>(null);

    const handleDensityChange = (densityKey: string) => {
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
