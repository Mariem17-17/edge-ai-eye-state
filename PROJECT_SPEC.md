# Hardware-Aware Eye-State Classification

## 1. Problem statement

This project addresses binary eye-state classification as one component of a driver-monitoring pipeline. Given a cropped eye image, the model predicts whether the eye is open or closed. The classifier may later be integrated with face and eye localization, followed by temporal reasoning to identify prolonged eye-closure events. The initial project focuses on model quality, optimization, C++ inference, and deployment-oriented evaluation rather than delivering a complete driver-monitoring or safety system.


## 2. Project objective

Develop and evaluate a reproducible eye-state classification pipeline, optimize the trained model for resource-constrained execution, and integrate the resulting inference workflow into a C++ application. The project will include reproducible data preparation, an FP32 baseline, INT8 quantization, one additional optimization method, Python and C++ inference, model comparison, testing, host-side benchmarking, and a video demonstration.

## 3. Initial scope

The initial scope includes developing a binary classifier trained on cropped eye images from a public dataset. A subject-aware or leakage-aware train, validation, and test split will be used where dataset metadata allows it. The project will compare an FP32 baseline, an INT8-quantized model, and one additionally optimized model. Python and C++ inference pipelines will be implemented and compared using image-level evaluation, host-side benchmarks, and numerical consistency tests. A recorded-video or webcam demonstration and a deployment-constraint analysis will complete the first version.
## 4. Non-goals

- Complete drowsiness diagnosis
- Medical or safety certification
- Deployment on physical MCU hardware
- Measured MCU latency
- Measured power consumption
- Complete automotive production integration
- Training a face detector from scratch
- Comparing ten deep-learning architectures
- Supporting every camera and lighting condition
- Claiming real-time target performance without target hardware

## 5. Success metrics

The project will be evaluated using four categories of metrics.

### Predictive metrics
For binary metric calculation, the closed-eye class will initially be treated as the positive class:

- Positive class: closed
- Negative class: open

- Accuracy
- Precision
- Recall
- F1 score
- Confusion matrix
- Closed-to-open error rate: closed eye predicted as open
- Open-to-closed error rate: open eye predicted as closed

### Optimization metrics

- Model file size
- Performance loss after quantization
- Host inference latency
- Supported operations
- Python/C++ output consistency

### Engineering metrics

- Tests passing
- Reproducible environment
- Reproducible data split
- Automated benchmark command
- Clean CMake build
- CI passing

### Deployment-oriented metrics

The following are provisional design targets for the first implementation. They are not validated hardware requirements and may be revised after dataset inspection and baseline experimentation. 
1. Model file size: less than 5 MB
2. Input resolution: no more than 128 × 128 initially
3. Quantized format: INT8-compatible
4. Accuracy/F1 degradation: less than 2 percentage points from baseline

## 6. Deployment assumptions

The first implementation will be tested on a host computer.
The results are split into 3 categories:
### Measured

- Model file size
- Predictive metrics
- Host latency
- Python/C++ output differences

### Estimated or constrained by design

- Maximum model budget
- Candidate memory assumptions
- Edge-compatible operator choices

### Not validated

- MCU latency
- Target RAM consumption
- Power consumption
- Camera/display integration
- Hardware acceleration
- Real-time guarantees

## 7. Known limitations

The initial project has the following known limitations:
- No physical embedded target
- Public dataset may not represent real driving conditions
- Cropped eye images simplify the full problem
- Performance may depend on eye-localization quality
- Lighting, glasses, reflections, head pose, and image quality may affect predictions
- A binary image classifier does not by itself detect drowsiness
- Host latency cannot be presented as embedded-target latency

## 8. Planned deliverables
By the end of the project, the following deliverables are expected:
- Dataset analysis report
- Reproducible train/validation/test split
- FP32 baseline model
- Quantized model
- Additional optimized model
- Evaluation report
- Failure-case analysis
- Python inference pipeline
- C++ inference application
- Python/C++ consistency tests
- Host-side benchmark
- Video demonstration
- Unit and integration tests
- Continuous integration workflow
- Architecture diagram
- Complete README
- Physical-target validation plan