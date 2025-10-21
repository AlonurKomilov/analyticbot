import React from 'react';
import { Grid, Box, Button } from '@mui/material';
import ModernCard, { ModernCardHeader } from '../../common/ModernCard';
import {
    ValidatedTextField,
    ValidatedSelect,
    FormSection,
    FormActions
} from '../../common/forms';
import { useFormValidation } from '../../common/forms';

interface Channel {
    id: string | number;
    title: string;
    username: string;
}

interface FormValues {
    text: string;
    selectedChannel: string;
    scheduleTime: string;
}

interface PostCreatorFormProps {
    channels?: Channel[];
    onSubmit?: (formData: FormValues) => Promise<void> | void;
    onSchedule?: (formData: FormValues) => Promise<void> | void;
    loading?: boolean;
}

/**
 * PostCreatorForm - Modernized post creation form
 *
 * Demonstrates the new form components and validation system.
 * Reduced complexity by using reusable form patterns.
 */
const PostCreatorForm: React.FC<PostCreatorFormProps> = ({
    channels = [],
    onSubmit,
    onSchedule,
    loading = false
}) => {
    // Form validation rules
    const validationRules = {
        text: {
            required: true,
            maxLength: 4096,
            requiredMessage: 'Please add some text for your post',
            maxLengthMessage: 'Post text cannot exceed 4096 characters'
        },
        selectedChannel: {
            required: true,
            requiredMessage: 'Please select a channel to post to'
        },
        scheduleTime: {
            required: true,
            requiredMessage: 'Please select when to publish this post',
            custom: (value: string) => {
                if (value && new Date(value) <= new Date()) {
                    return 'Please choose a time in the future';
                }
                return '';
            }
        }
    };

    // Use our form validation hook
    const {
        values,
        errors,
        handleChange,
        handleBlur,
        handleSubmit,
        resetForm,
        isValid
    } = useFormValidation({
        text: '',
        selectedChannel: '',
        scheduleTime: ''
    }, validationRules);

    // Channel options for select
    const channelOptions = channels.map(channel => ({
        value: channel.id.toString(),
        label: `${channel.title} (@${channel.username})`
    }));

    const handleFormSubmit = (): void => {
        handleSubmit(async (formData: any) => {
            await onSubmit?.(formData as FormValues);
        });
    };

    const handleSchedulePost = (): void => {
        handleSubmit(async (formData: any) => {
            await onSchedule?.(formData as FormValues);
        });
    };

    return (
        <ModernCard variant="elevated">
            <ModernCardHeader
                title="Create New Post"
                subtitle="Compose and schedule your content"
            />

            <Box component="form">
                <FormSection
                    title="Content"
                    subtitle="Write your post content"
                    required
                >
                    <ValidatedTextField
                        name="text"
                        label="Post Text"
                        placeholder="What would you like to share?"
                        multiline
                        rows={4}
                        value={(values as any).text}
                        onChange={handleChange}
                        onBlur={handleBlur}
                        errors={errors}
                        showCharacterCount
                        maxLength={4096}
                        required
                    />
                </FormSection>

                <Grid container spacing={3}>
                    <Grid item xs={12} md={6}>
                        <FormSection title="Channel" required>
                            <ValidatedSelect
                                name="selectedChannel"
                                label="Select Channel"
                                placeholder="Choose a channel..."
                                options={channelOptions}
                                value={(values as any).selectedChannel}
                                onChange={handleChange}
                                onBlur={handleBlur}
                                errors={errors}
                                required
                            />
                        </FormSection>
                    </Grid>

                    <Grid item xs={12} md={6}>
                        <FormSection title="Schedule" required>
                            <ValidatedTextField
                                name="scheduleTime"
                                label="Publish Time"
                                type="datetime-local"
                                value={(values as any).scheduleTime}
                                onChange={handleChange}
                                onBlur={handleBlur}
                                errors={errors}
                                required
                                InputLabelProps={{
                                    shrink: true,
                                }}
                            />
                        </FormSection>
                    </Grid>
                </Grid>

                <Box sx={{
                    borderTop: '1px solid',
                    borderColor: 'divider',
                    pt: 3,
                    mt: 3,
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center'
                }}>
                    <Button
                        variant="outlined"
                        onClick={handleSchedulePost}
                        disabled={!isValid || loading}
                    >
                        Schedule Post
                    </Button>

                    <FormActions
                        onSubmit={handleFormSubmit}
                        onCancel={resetForm}
                        submitLabel="Post Now"
                        cancelLabel="Clear Form"
                        loading={loading}
                        disabled={!isValid}
                        align="right"
                    />
                </Box>
            </Box>
        </ModernCard>
    );
};

export default PostCreatorForm;
