
import React, { useState, useEffect } from "react";
import {
    Box,
    Typography,
    Paper,
    Chip,
    CircularProgress,
    Button,
    Grid,
    Card,
    CardContent,
    useTheme,
    alpha,
    IconButton,
    Menu,
    MenuItem,
    ListItemIcon,
    ListItemText
} from "@mui/material";
import {
    Visibility,
    MoreVert,
    Add,
    AccountBalanceWallet,
    TrendingUp,
    MoneyOff
} from "@mui/icons-material";
import { DataGrid, GridColDef, GridRenderCellParams } from "@mui/x-data-grid";
import { useNavigate } from "react-router-dom";
import { savingsApi } from "@/api/savings.api";
import { SavingsAccount } from "@/types/savings.types";

const SavingsAccounts: React.FC = () => {
    const theme = useTheme();
    const navigate = useNavigate();
    const [accounts, setAccounts] = useState<SavingsAccount[]>([]);
    const [loading, setLoading] = useState(true);
    const [totalCount, setTotalCount] = useState(0);
    const [page, setPage] = useState(0);
    const [pageSize, setPageSize] = useState(10);
    const [actionsMenuAnchor, setActionsMenuAnchor] = useState<null | HTMLElement>(null);
    const [actionsAccountId, setActionsAccountId] = useState<number | null>(null);

    const fetchAccounts = async () => {
        setLoading(true);
        try {
            const data = await savingsApi.getAccounts({ page: page + 1 });
            setAccounts(data.results);
            setTotalCount(data.count);
        } catch (error) {
            console.error("Error fetching savings accounts:", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchAccounts();
    }, [page, pageSize]);

    const handleActionsClick = (event: React.MouseEvent<HTMLButtonElement>, id: number) => {
        event.stopPropagation();
        setActionsMenuAnchor(event.currentTarget);
        setActionsAccountId(id);
    };

    const handleActionsClose = () => {
        setActionsMenuAnchor(null);
        setActionsAccountId(null);
    };

    const columns: GridColDef[] = [
        { field: 'account_number', headerName: 'Account Number', width: 180 },
        { field: 'account_type', headerName: 'Type', width: 150 },
        {
            field: 'balance',
            headerName: 'Balance',
            width: 150,
            valueFormatter: (params) => {
                if (params.value == null) {
                    return '';
                }
                return `Ugx ${params.value.toLocaleString()}`;
            },
        },
        {
            field: 'status',
            headerName: 'Status',
            width: 120,
            renderCell: (params: GridRenderCellParams) => {
                const status = params.value as string;
                let color = "default";
                if (status === "ACTIVE") color = "success";
                else if (status === "DORMANT") color = "warning";
                else if (status === "CLOSED") color = "error";

                return <Chip label={status} color={color as any} size="small" />;
            }
        },
        {
            field: 'interest_rate',
            headerName: 'Interest Rate',
            width: 120,
            valueGetter: (params) => `${params.row.interest_rate}%`
        },
        {
            field: 'date_opened',
            headerName: 'Date Opened',
            width: 150,
            valueGetter: (params) => new Date(params.row.date_opened).toLocaleDateString()
        },
        {
            field: 'actions',
            headerName: 'Actions',
            width: 80,
            sortable: false,
            renderCell: (params) => (
                <IconButton onClick={(e) => handleActionsClick(e, params.row.id)}>
                    <MoreVert />
                </IconButton>
            )
        }
    ];

    const totalBalance = accounts.reduce((sum, acc) => sum + acc.balance, 0);

    return (
        <Box>
            <Grid container spacing={3} alignItems="center" sx={{ mb: 3 }}>
                <Grid item xs={12} md={6}>
                    <Typography variant="h5" fontWeight={700} color="primary.main">
                        Savings Accounts
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                        Manage member savings accounts
                    </Typography>
                </Grid>
                <Grid item xs={12} md={6} display="flex" justifyContent="flex-end">
                    <Button variant="contained" startIcon={<Add />} onClick={() => console.log("New Account")}>
                        New Account
                    </Button>
                </Grid>
            </Grid>

            {/* Stats */}
            <Grid container spacing={3} sx={{ mb: 3 }}>
                <Grid item xs={12} md={4}>
                    <Card variant="outlined">
                        <CardContent sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                            <Avatar sx={{ bgcolor: alpha(theme.palette.primary.main, 0.1), color: 'primary.main', width: 56, height: 56 }}>
                                <AccountBalanceWallet />
                            </Avatar>
                            <Box>
                                <Typography color="text.secondary" variant="body2">Total Savings</Typography>
                                <Typography variant="h5" fontWeight="bold">Ugx {totalBalance.toLocaleString()}</Typography>
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>
                <Grid item xs={12} md={4}>
                    <Card variant="outlined">
                        <CardContent sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                            <Avatar sx={{ bgcolor: alpha(theme.palette.success.main, 0.1), color: 'success.main', width: 56, height: 56 }}>
                                <TrendingUp />
                            </Avatar>
                            <Box>
                                <Typography color="text.secondary" variant="body2">Total Interest Paid</Typography>
                                <Typography variant="h5" fontWeight="bold">Ugx 0</Typography>
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>

            <Paper sx={{ width: '100%', height: 500 }}>
                <DataGrid
                    rows={accounts}
                    columns={columns}
                    rowCount={totalCount}
                    loading={loading}
                    paginationMode="server"
                    paginationModel={{ page, pageSize }}
                    onPaginationModelChange={(newModel) => {
                        setPage(newModel.page);
                        setPageSize(newModel.pageSize);
                    }}
                    pageSizeOptions={[10, 25, 50]}
                    disableRowSelectionOnClick
                />
            </Paper>

            <Menu
                anchorEl={actionsMenuAnchor}
                open={Boolean(actionsMenuAnchor)}
                onClose={handleActionsClose}
            >
                <MenuItem onClick={() => {
                    if (actionsAccountId) navigate(`/savings/${actionsAccountId}`);
                    handleActionsClose();
                }}>
                    <ListItemIcon><Visibility fontSize="small" /></ListItemIcon>
                    <ListItemText>View Details</ListItemText>
                </MenuItem>
                <MenuItem onClick={handleActionsClose}>
                    <ListItemIcon><MoneyOff fontSize="small" /></ListItemIcon>
                    <ListItemText>Withdraw</ListItemText>
                </MenuItem>
            </Menu>
        </Box>
    );
};

export default SavingsAccounts;
