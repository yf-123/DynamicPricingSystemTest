import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Button, Table, Statistic, message, Spin } from 'antd';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import axios from 'axios';

const ModelMonitoring = () => {
    const [loading, setLoading] = useState(false);
    const [modelInfo, setModelInfo] = useState(null);
    const [trainingHistory, setTrainingHistory] = useState([]);
    const [featureImportance, setFeatureImportance] = useState([]);

    const fetchModelInfo = async () => {
        try {
            const response = await axios.get('/api/pricing/model/info');
            if (response.data.success) {
                setModelInfo(response.data.model_info);
                setFeatureImportance(response.data.model_info.feature_importance || []);
            }
        } catch (error) {
            message.error('Failed to fetch model information');
        }
    };

    const handleTrainModel = async () => {
        setLoading(true);
        try {
            const response = await axios.post('/api/pricing/model/train');
            if (response.data.success) {
                message.success('Model trained successfully');
                fetchModelInfo();
            } else {
                message.error(response.data.error || 'Training failed');
            }
        } catch (error) {
            message.error('Failed to train model');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchModelInfo();
    }, []);

    const featureColumns = [
        {
            title: 'Feature',
            dataIndex: 'feature',
            key: 'feature',
        },
        {
            title: 'Importance',
            dataIndex: 'importance',
            key: 'importance',
            render: (value) => `${(value * 100).toFixed(2)}%`,
        },
    ];

    return (
        <div className="model-monitoring">
            <Row gutter={[16, 16]}>
                <Col span={24}>
                    <Card title="Model Performance">
                        <Row gutter={16}>
                            <Col span={6}>
                                <Statistic
                                    title="R² Score"
                                    value={modelInfo?.r2_score || 0}
                                    precision={3}
                                />
                            </Col>
                            <Col span={6}>
                                <Statistic
                                    title="MSE"
                                    value={modelInfo?.mse || 0}
                                    precision={3}
                                />
                            </Col>
                            <Col span={6}>
                                <Statistic
                                    title="Training Samples"
                                    value={modelInfo?.training_samples || 0}
                                />
                            </Col>
                            <Col span={6}>
                                <Statistic
                                    title="Last Training"
                                    value={modelInfo?.last_training || 'Never'}
                                />
                            </Col>
                        </Row>
                    </Card>
                </Col>

                <Col span={24}>
                    <Card
                        title="Feature Importance"
                        extra={
                            <Button
                                type="primary"
                                onClick={handleTrainModel}
                                loading={loading}
                            >
                                Retrain Model
                            </Button>
                        }
                    >
                        <Table
                            dataSource={featureImportance}
                            columns={featureColumns}
                            rowKey="feature"
                            pagination={false}
                        />
                    </Card>
                </Col>

                {modelInfo?.training_history && (
                    <Col span={24}>
                        <Card title="Training History">
                            <LineChart
                                width={800}
                                height={300}
                                data={modelInfo.training_history}
                                margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                            >
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="date" />
                                <YAxis />
                                <Tooltip />
                                <Legend />
                                <Line
                                    type="monotone"
                                    dataKey="r2_score"
                                    stroke="#8884d8"
                                    name="R² Score"
                                />
                                <Line
                                    type="monotone"
                                    dataKey="mse"
                                    stroke="#82ca9d"
                                    name="MSE"
                                />
                            </LineChart>
                        </Card>
                    </Col>
                )}
            </Row>
        </div>
    );
};

export default ModelMonitoring; 