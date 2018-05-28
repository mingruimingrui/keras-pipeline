import os
import sys
import argparse

import keras
import tensorflow as tf

if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    import keras_pipeline
    __package__ = "keras_pipeline"

# Model
from keras_pipeline.models import RetinaNetConfig, RetinaNetTrain, RetinaNetFromTrain

# Data generator
from keras_pipeline.generators.coco import CocoDetectionGenerator
from keras_pipeline.preprocessing.transform import random_transform_generator

# Evaluation callbacks
from keras_pipeline.callbacks import RedirectModel
from keras_pipeline.callbacks.eval import Evaluate


def makedirs(path):
    if not os.path.isdir(path):
        os.makedirs(path)


def create_callback(training_model, prediction_model, validation_generator, args):
    callbacks = []

    tensorboard_callback = None

    if args.tensorboard_dir:
        makedirs(args.tensorboard_dir)
        tensorboard_callback = keras.callbacks.TensorBoard(
            log_dir                = args.tensorboard_dir,
            histogram_freq         = 0,
            batch_size             = args.batch_size,
            write_graph            = True,
            write_grads            = False,
            write_images           = False,
            embeddings_freq        = 0,
            embeddings_layer_names = None,
            embeddings_metadata    = None
        )
        callbacks.append(tensorboard_callback)

    # Save model
    if args.snapshots:
        # ensure directory created first; otherwise h5py will error after epoch.
        makedirs(args.snapshot_path)
        checkpoint = keras.callbacks.ModelCheckpoint(
            os.path.join(
                args.snapshot_path,
                'Inception_COCO_{{epoch:02d}}.h5'
            ),
            verbose=1,
            # save_best_only=True,
            # monitor="mAP",
            # mode='max'
        )
        # checkpoint = RedirectModel(checkpoint, training_model)
        callbacks.append(checkpoint)

    if args.evaluation:
        evaluation = Evaluate(validation_generator, tensorboard=tensorboard_callback)
        evaluation = RedirectModel(evaluation, prediction_model)
        callbacks.append(evaluation)

    callbacks.append(keras.callbacks.ReduceLROnPlateau(
        monitor  = 'loss',
        factor   = 0.1,
        patience = 2,
        verbose  = 1,
        mode     = 'auto',
        epsilon  = 0.0001,
        cooldown = 0,
        min_lr   = 0
    ))

    return callbacks


def create_models(args, model_config):
    training_model = RetinaNetTrain(model_config)
    prediction_model = RetinaNetFromTrain(training_model, model_config)

    return training_model, prediction_model



def create_generators(args, model_config):
    transform_generator = random_transform_generator(
        min_rotation=-0.1,
        max_rotation=0.1,
        min_translation=(-0.1, -0.1),
        max_translation=(0.1, 0.1),
        min_shear=-0.1,
        max_shear=0.1,
        min_scaling=(0.9, 0.9),
        max_scaling=(1.1, 1.1),
        flip_x_chance=0.5,
        flip_y_chance=0.5,
    )

    train_generator = CocoDetectionGenerator(
        args.coco_path,
        'train2017',
        batch_size = args.batch_size,
        compute_anchors = model_config.compute_anchors,
        transform_generator=transform_generator
    )

    validation_generator = CocoDetectionGenerator(
        args.coco_path,
        'val2017',
        batch_size = args.batch_size,
        compute_anchors = model_config.compute_anchors
    )

    return train_generator, validation_generator


def config_session():
    session_config = tf.ConfigProto()

    # Allow growth
    session_config.gpu_options.allow_growth = True

    # Set config
    current_session = tf.Session(config=session_config)
    keras.backend.tensorflow_backend.set_session(current_session)


def validate_requirements():
    # Check that system has GPU
    from tensorflow.python.client import device_lib
    local_devices = device_lib.list_local_devices()
    assert 'GPU' in [d.device_type for d in local_devices], 'Training must be using GPU'


def setup():
    validate_requirements()
    config_session()


def check_args(args):
    assert args.coco_path is not None, 'Must have the COCO dataset'
    assert args.num_gpu >= 1, 'Must train with atleast 1 GPU'
    assert args.batch_size >= args.num_gpu, 'Batch size must be equal or greater than number of GPUs used'

    return args


def parse_args(args):
    parser = argparse.ArgumentParser(description='Demo training script for training a RetinaNet network.')

    # Resume training / load weights
    # TODO: Allow resumption of training and loading of weights
    # parser.add_argument('--snapshot',
    #     help='Resume training from a snapshot file')

    # Most frequently used params
    parser.add_argument('--num-gpu',
        help='Number of gpus to train model with, you must train with atleast 1 GPU',
        default=1, type=int)
    parser.add_argument('--batch-size',
        help='Size of the batches',
        default=1, type=int)
    parser.add_argument('--coco-path',
        help='Path to dataset directory (ie. /tmp/COCO)',
        type=str)

    # Logging params
    parser.add_argument('--snapshot-path',
        help='Path to store snapshots of model during training',
        default='./snapshot')
    parser.add_argument('--no-snapshots',
        help='Disable saving snapshots',
        dest='snapshots', action='store_false')
    parser.add_argument('--tensorboard-dir',
        help='Log directory for Tensorboard output',
        default='./logs')
    parser.add_argument('--no-evaluation',
        help='Disable per epoch evaluation',
        dest='evaluation', action='store_false')
    parser.add_argument('--freeze-backbone',
        help='Freeze training of backbone layers',
        action='store_true')

    return parser.parse_args(args)


def get_args(args):
    return check_args(parse_args(args))


def main():
    # Set up script options
    args = get_args(sys.argv[1:])
    setup()

    print('\n==== Begining training of the demo retinanet model ====')

    # Create a dataset generator config file
    # TODO: add dataset generator config
    # CocoDetectionGeneratorConfig

    # Create a model config object to store information on model
    # TODO: call num_classes from GeneratorConfig
    model_config = RetinaNetConfig(num_classes = 80)

    # Create data generator
    # TODO: add dataset generator config
    train_generator, validation_generator = create_generators(args, model_config)

    # Create training model
    print('\n==== Creating Model ====')
    print('This can take a while...')
    training_model, prediction_model = create_models(args, model_config)
    print('Model created')

    # Create callback
    callbacks = create_callback(training_model, prediction_model, validation_generator, args)

    # start_training
    print('\n==== Training Model ====')
    training_model.fit_generator(
        generator=train_generator,
        steps_per_epoch=10000,
        epochs=50,
        verbose=1,
        callbacks=callbacks,
    )


if __name__ == '__main__':
    main()
