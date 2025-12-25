
import React, { useState } from "react";
import {
    Box,
    Typography,
    TextField,
    Button,
    Grid,
    Card,
    CardContent,
    MenuItem,
    Stack,
    Divider,
} from "@mui/material";
import { useNavigate } from "react-router-dom";
import { useForm, Controller, useFieldArray } from "react-hook-form";
import { membersApi } from "@/api/members.api";
import { MemberRegistrationRequest } from "@/types/member.types";

const AddMember: React.FC = () => {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);

    const { control, handleSubmit, register, formState: { errors } } = useForm<MemberRegistrationRequest>({
        defaultValues: {
            member: {
                membership_type: "INDIVIDUAL",
                marital_status: "SINGLE",
                employment_status: "EMPLOYED",
                city: "",
                district: "",
                national_id: "",
                occupation: "",
                physical_address: "",
                monthly_income: 0,
                date_of_birth: "",
            },
            next_of_kin: [
                {
                    full_name: "",
                    relationship: "SPOUSE",
                    phone_number: "",
                    physical_address: "",
                    national_id: "",
                    percentage_share: 100,
                },
            ],
        },
    });

    const { fields, append, remove } = useFieldArray({
        control,
        name: "next_of_kin",
    });

    const onSubmit = async (data: MemberRegistrationRequest) => {
        setLoading(true);
        try {
            await membersApi.createMember(data);
            navigate("/members");
        } catch (error) {
            console.error("Error creating member:", error);
            // alert("Failed to create member");
        } finally {
            setLoading(false);
        }
    };

    return (
        <Box>
            <Box sx={{ mb: 3 }}>
                <Typography variant="h5" fontWeight={700} color="primary.main">
                    Add New Member
                </Typography>
                <Typography variant="body2" color="text.secondary">
                    Register a new member to the SACCO
                </Typography>
            </Box>

            <form onSubmit={handleSubmit(onSubmit)}>
                <Grid container spacing={3}>
                    <Grid item xs={12} md={8}>
                        <Card variant="outlined" sx={{ mb: 3 }}>
                            <CardContent>
                                <Typography variant="h6" sx={{ mb: 2 }}>
                                    Personal Information
                                </Typography>
                                <Grid container spacing={2}>
                                    <Grid item xs={12} sm={6}>
                                        <TextField
                                            fullWidth
                                            label="Date of Birth"
                                            type="date"
                                            InputLabelProps={{ shrink: true }}
                                            {...register("member.date_of_birth", { required: "Required" })}
                                            error={!!errors.member?.date_of_birth}
                                            helperText={errors.member?.date_of_birth?.message}
                                        />
                                    </Grid>
                                    <Grid item xs={12} sm={6}>
                                        <Controller
                                            name="member.marital_status"
                                            control={control}
                                            render={({ field }) => (
                                                <TextField {...field} select fullWidth label="Marital Status">
                                                    <MenuItem value="SINGLE">Single</MenuItem>
                                                    <MenuItem value="MARRIED">Married</MenuItem>
                                                    <MenuItem value="DIVORCED">Divorced</MenuItem>
                                                    <MenuItem value="WIDOWED">Widowed</MenuItem>
                                                </TextField>
                                            )}
                                        />
                                    </Grid>
                                    <Grid item xs={12} sm={6}>
                                        <TextField
                                            fullWidth
                                            label="National ID / Passport"
                                            {...register("member.national_id", { required: "Required" })}
                                        />
                                    </Grid>
                                    <Grid item xs={12} sm={6}>
                                        <Controller
                                            name="member.membership_type"
                                            control={control}
                                            render={({ field }) => (
                                                <TextField {...field} select fullWidth label="Membership Type">
                                                    <MenuItem value="INDIVIDUAL">Individual</MenuItem>
                                                    <MenuItem value="JOINT">Joint</MenuItem>
                                                    <MenuItem value="CORPORATE">Corporate</MenuItem>
                                                </TextField>
                                            )}
                                        />
                                    </Grid>
                                </Grid>
                            </CardContent>
                        </Card>

                        <Card variant="outlined" sx={{ mb: 3 }}>
                            <CardContent>
                                <Typography variant="h6" sx={{ mb: 2 }}>
                                    Contact & Address
                                </Typography>
                                <Grid container spacing={2}>
                                    <Grid item xs={12}>
                                        <TextField
                                            fullWidth
                                            label="Physical Address"
                                            {...register("member.physical_address", { required: "Required" })}
                                        />
                                    </Grid>
                                    <Grid item xs={12} sm={6}>
                                        <TextField
                                            fullWidth
                                            label="City"
                                            {...register("member.city", { required: "Required" })}
                                        />
                                    </Grid>
                                    <Grid item xs={12} sm={6}>
                                        <TextField
                                            fullWidth
                                            label="District"
                                            {...register("member.district", { required: "Required" })}
                                        />
                                    </Grid>
                                    <Grid item xs={12}>
                                        <TextField
                                            fullWidth
                                            label="Postal Address (Optional)"
                                            {...register("member.postal_address")}
                                        />
                                    </Grid>
                                </Grid>
                            </CardContent>
                        </Card>

                        <Card variant="outlined" sx={{ mb: 3 }}>
                            <CardContent>
                                <Typography variant="h6" sx={{ mb: 2 }}>
                                    Employment
                                </Typography>
                                <Grid container spacing={2}>
                                    <Grid item xs={12} sm={6}>
                                        <Controller
                                            name="member.employment_status"
                                            control={control}
                                            render={({ field }) => (
                                                <TextField {...field} select fullWidth label="Employment Status">
                                                    <MenuItem value="EMPLOYED">Employed</MenuItem>
                                                    <MenuItem value="SELF_EMPLOYED">Self Employed</MenuItem>
                                                    <MenuItem value="UNEMPLOYED">Unemployed</MenuItem>
                                                    <MenuItem value="RETIRED">Retired</MenuItem>
                                                    <MenuItem value="STUDENT">Student</MenuItem>
                                                    <MenuItem value="OTHER">Other</MenuItem>
                                                </TextField>
                                            )}
                                        />
                                    </Grid>
                                    <Grid item xs={12} sm={6}>
                                        <TextField
                                            fullWidth
                                            label="Occupation"
                                            {...register("member.occupation", { required: "Required" })}
                                        />
                                    </Grid>
                                    <Grid item xs={12} sm={6}>
                                        <TextField
                                            fullWidth
                                            label="Monthly Income"
                                            type="number"
                                            {...register("member.monthly_income", { required: "Required", valueAsNumber: true })}
                                        />
                                    </Grid>
                                </Grid>
                            </CardContent>
                        </Card>

                        <Card variant="outlined" sx={{ mb: 3 }}>
                            <CardContent>
                                <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                                    <Typography variant="h6">Next of Kin</Typography>
                                    <Button variant="outlined" size="small" onClick={() => append({
                                        full_name: "",
                                        relationship: "SPOUSE",
                                        phone_number: "",
                                        physical_address: "",
                                        national_id: "",
                                        percentage_share: 0
                                    })}>
                                        Add Beneficiary
                                    </Button>
                                </Box>
                                {fields.map((field, index) => (
                                    <Box key={field.id} sx={{ mb: 2, p: 2, border: '1px dashed grey', borderRadius: 1 }}>
                                        <Grid container spacing={2}>
                                            <Grid item xs={12} sm={6}>
                                                <TextField fullWidth label="Full Name" {...register(`next_of_kin.${index}.full_name` as const, { required: true })} />
                                            </Grid>
                                            <Grid item xs={12} sm={6}>
                                                <Controller
                                                    name={`next_of_kin.${index}.relationship` as const}
                                                    control={control}
                                                    render={({ field }) => (
                                                        <TextField {...field} select fullWidth label="Relationship">
                                                            <MenuItem value="SPOUSE">Spouse</MenuItem>
                                                            <MenuItem value="CHILD">Child</MenuItem>
                                                            <MenuItem value="PARENT">Parent</MenuItem>
                                                            <MenuItem value="SIBLING">Sibling</MenuItem>
                                                            <MenuItem value="OTHER">Other</MenuItem>
                                                        </TextField>
                                                    )}
                                                />
                                            </Grid>
                                            <Grid item xs={12} sm={6}>
                                                <TextField fullWidth label="Phone Number" {...register(`next_of_kin.${index}.phone_number` as const, { required: true })} />
                                            </Grid>
                                            <Grid item xs={12} sm={6}>
                                                <TextField fullWidth label="National ID" {...register(`next_of_kin.${index}.national_id` as const, { required: true })} />
                                            </Grid>
                                            <Grid item xs={12} sm={6}>
                                                <TextField fullWidth label="Physical Address" {...register(`next_of_kin.${index}.physical_address` as const, { required: true })} />
                                            </Grid>
                                            <Grid item xs={12} sm={6}>
                                                <TextField fullWidth label="% Share" type="number" {...register(`next_of_kin.${index}.percentage_share` as const, { required: true, valueAsNumber: true })} />
                                            </Grid>
                                            <Grid item xs={12}>
                                                <Button color="error" onClick={() => remove(index)}>Remove</Button>
                                            </Grid>
                                        </Grid>
                                    </Box>
                                ))}
                            </CardContent>
                        </Card>

                        <Stack direction="row" spacing={2} justifyContent="flex-end">
                            <Button variant="outlined" onClick={() => navigate("/members")}>Cancel</Button>
                            <Button variant="contained" type="submit" disabled={loading}>
                                {loading ? "Registering..." : "Register Member"}
                            </Button>
                        </Stack>
                    </Grid>
                </Grid>
            </form>
        </Box>
    );
};

export default AddMember;
