
import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
    Box,
    Typography,
    Grid,
    Card,
    CardContent,
    CircularProgress,
    Button,
    Chip,
    Divider,
    Avatar,
    Tab,
    Tabs,
} from "@mui/material";
import { ArrowBack, Edit, Person } from "@mui/icons-material";
import { membersApi } from "@/api/members.api";
import { Member } from "@/types/member.types";

interface TabPanelProps {
    children?: React.ReactNode;
    index: number;
    value: number;
}

function CustomTabPanel(props: TabPanelProps) {
    const { children, value, index, ...other } = props;

    return (
        <div
            role="tabpanel"
            hidden={value !== index}
            id={`simple-tabpanel-${index}`}
            aria-labelledby={`simple-tab-${index}`}
            {...other}
        >
            {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
        </div>
    );
}

const MemberProfile: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const [member, setMember] = useState<Member | null>(null);
    const [loading, setLoading] = useState(true);
    const [tabValue, setTabValue] = useState(0);

    useEffect(() => {
        const fetchMember = async () => {
            try {
                if (id) {
                    const data = await membersApi.getMember(parseInt(id));
                    setMember(data);
                }
            } catch (error) {
                console.error("Error fetching member details:", error);
            } finally {
                setLoading(false);
            }
        };
        fetchMember();
    }, [id]);

    const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
        setTabValue(newValue);
    };

    if (loading) {
        return (
            <Box display="flex" justifyContent="center" alignItems="center" height="50vh">
                <CircularProgress />
            </Box>
        );
    }

    if (!member) {
        return <Typography>Member not found.</Typography>;
    }

    return (
        <Box>
            <Button startIcon={<ArrowBack />} onClick={() => navigate("/members")} sx={{ mb: 2 }}>
                Back to Members
            </Button>

            <Grid container spacing={3}>
                {/* Left Column: Summary Card */}
                <Grid item xs={12} md={4}>
                    <Card variant="outlined">
                        <CardContent sx={{ textAlign: "center" }}>
                            <Avatar
                                sx={{ width: 100, height: 100, margin: "0 auto", mb: 2, bgcolor: "primary.main" }}
                            >
                                <Person fontSize="large" />
                            </Avatar>
                            <Typography variant="h5" fontWeight="bold">
                                {member.user?.first_name} {member.user?.last_name}
                            </Typography>
                            <Typography color="text.secondary" gutterBottom>
                                {member.member_number}
                            </Typography>
                            <Chip
                                label={member.membership_status}
                                color={member.membership_status === "ACTIVE" ? "success" : "default"}
                                size="small"
                                sx={{ mt: 1 }}
                            />
                            <Divider sx={{ my: 2 }} />
                            <Box textAlign="left">
                                <Typography variant="body2" color="text.secondary">
                                    Email
                                </Typography>
                                <Typography variant="body1" gutterBottom>
                                    {member.user?.email}
                                </Typography>
                                <Typography variant="body2" color="text.secondary">
                                    Phone
                                </Typography>
                                <Typography variant="body1" gutterBottom>
                                    {member.user?.phone_number}
                                </Typography>
                                <Typography variant="body2" color="text.secondary">
                                    Joined
                                </Typography>
                                <Typography variant="body1">
                                    {new Date(member.registration_date).toLocaleDateString()}
                                </Typography>
                            </Box>
                            <Button
                                variant="outlined"
                                startIcon={<Edit />}
                                fullWidth
                                sx={{ mt: 2 }}
                                onClick={() => console.log("Edit member")}
                            >
                                Edit Profile
                            </Button>
                        </CardContent>
                    </Card>
                </Grid>

                {/* Right Column: Detailed Tabs */}
                <Grid item xs={12} md={8}>
                    <Card variant="outlined">
                        <Box sx={{ borderBottom: 1, borderColor: "divider" }}>
                            <Tabs value={tabValue} onChange={handleTabChange}>
                                <Tab label="Personal Details" />
                                <Tab label="Employment" />
                                <Tab label="Next of Kin" />
                                <Tab label="Documents" />
                            </Tabs>
                        </Box>
                        <CustomTabPanel value={tabValue} index={0}>
                            <Grid container spacing={2}>
                                <Grid item xs={6}>
                                    <Typography variant="subtitle2" color="text.secondary">Date of Birth</Typography>
                                    <Typography>{member.date_of_birth}</Typography>
                                </Grid>
                                <Grid item xs={6}>
                                    <Typography variant="subtitle2" color="text.secondary">Marital Status</Typography>
                                    <Typography>{member.marital_status}</Typography>
                                </Grid>
                                <Grid item xs={6}>
                                    <Typography variant="subtitle2" color="text.secondary">City</Typography>
                                    <Typography>{member.city}</Typography>
                                </Grid>
                                <Grid item xs={6}>
                                    <Typography variant="subtitle2" color="text.secondary">District</Typography>
                                    <Typography>{member.district}</Typography>
                                </Grid>
                                <Grid item xs={12}>
                                    <Typography variant="subtitle2" color="text.secondary">Physical Address</Typography>
                                    <Typography>{member.physical_address}</Typography>
                                </Grid>
                            </Grid>
                        </CustomTabPanel>
                        <CustomTabPanel value={tabValue} index={1}>
                            <Grid container spacing={2}>
                                <Grid item xs={6}>
                                    <Typography variant="subtitle2" color="text.secondary">Employment Status</Typography>
                                    <Typography>{member.employment_status}</Typography>
                                </Grid>
                                <Grid item xs={6}>
                                    <Typography variant="subtitle2" color="text.secondary">Occupation</Typography>
                                    <Typography>{member.occupation}</Typography>
                                </Grid>
                                <Grid item xs={6}>
                                    <Typography variant="subtitle2" color="text.secondary">Monthly Income</Typography>
                                    <Typography>{member.monthly_income?.toLocaleString()}</Typography>
                                </Grid>
                            </Grid>
                        </CustomTabPanel>
                        <CustomTabPanel value={tabValue} index={2}>
                            {member.next_of_kin?.map((nok) => (
                                <Box key={nok.id} mb={2} p={1} bgcolor="grey.50">
                                    <Typography variant="subtitle1" fontWeight="bold">{nok.full_name} ({nok.relationship})</Typography>
                                    <Typography variant="body2">{nok.phone_number}</Typography>
                                </Box>
                            ))}
                        </CustomTabPanel>
                        <CustomTabPanel value={tabValue} index={3}>
                            <Typography color="text.secondary">No documents uploaded yet.</Typography>
                        </CustomTabPanel>
                    </Card>
                </Grid>
            </Grid>
        </Box>
    );
};

export default MemberProfile;
