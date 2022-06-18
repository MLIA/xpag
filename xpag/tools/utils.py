# Copyright 2022 Nicolas Perrin-Gilbert.
#
# Licensed under the BSD 3-Clause License.

from enum import Enum
from typing import Tuple, Union, Dict, Any
import torch
import numpy as np
from jaxlib.xla_extension import DeviceArray
import jax.numpy as jnp


class DataType(Enum):
    TORCH_CPU = "data represented as torch tensors on CPU"
    TORCH_CUDA = "data represented as torch tensors on GPU"
    NUMPY = "data represented as numpy arrays"
    JAX = "data represented as jax DeviceArrays"


def get_datatype(x: Union[torch.Tensor, np.ndarray, DeviceArray]) -> DataType:
    if torch.is_tensor(x):
        if x.device.type == "cpu":
            return DataType.TORCH_CPU
        elif x.device.type == "cuda":
            return DataType.TORCH_CUDA
        else:
            raise TypeError(
                "PyTorch devices other than CPU or CUDA (e.g. XLA) " "are not handled."
            )
    elif isinstance(x, DeviceArray):
        return DataType.JAX
    elif isinstance(x, np.ndarray):
        return DataType.NUMPY
    else:
        raise TypeError(f"{type(x)} not handled.")


def datatype_convert(
    x: Union[torch.Tensor, np.ndarray, DeviceArray, list, float],
    datatype: Union[DataType, None] = DataType.NUMPY,
) -> Union[torch.Tensor, np.ndarray, DeviceArray]:
    if datatype is None:
        return x
    elif datatype == DataType.TORCH_CPU or datatype == DataType.TORCH_CUDA:
        if torch.is_tensor(x):
            if datatype == DataType.TORCH_CPU:
                return x.to(device="cpu")
            else:
                return x.to(device="cuda")
        elif isinstance(x, DeviceArray):
            if datatype == DataType.TORCH_CPU:
                return torch.tensor(np.array(x), device="cpu")
            else:
                return torch.tensor(np.array(x), device="cuda")
        else:
            if datatype == DataType.TORCH_CPU:
                return torch.tensor(x, device="cpu")
            else:
                return torch.tensor(x, device="cuda")
    elif datatype == DataType.NUMPY:
        if torch.is_tensor(x):
            return x.detach().cpu().numpy()
        elif isinstance(x, np.ndarray):
            return x
        else:
            return np.array(x)
    elif datatype == DataType.JAX:
        if torch.is_tensor(x):
            return jnp.array(x.detach().cpu().numpy())
        elif isinstance(x, DeviceArray):
            return x
        else:
            return jnp.array(x)


def reshape(
    x: Union[torch.Tensor, np.ndarray, DeviceArray, list, float],
    shape: Tuple[int, ...],
) -> Union[torch.Tensor, np.ndarray, DeviceArray]:
    if torch.is_tensor(x) or isinstance(x, np.ndarray) or isinstance(x, DeviceArray):
        return x.reshape(shape)
    else:
        return np.array(x).reshape(shape)


def hstack(
    x: Union[torch.Tensor, np.ndarray, DeviceArray],
    y: Union[torch.Tensor, np.ndarray, DeviceArray],
) -> Union[torch.Tensor, np.ndarray, DeviceArray]:
    if torch.is_tensor(x) and torch.is_tensor(y):
        return torch.hstack((x, y))
    elif isinstance(x, DeviceArray) and isinstance(y, DeviceArray):
        return jnp.hstack((x, y))
    else:
        return np.hstack((x, y))


def maximum(
    x: Union[torch.Tensor, np.ndarray, DeviceArray],
    y: Union[torch.Tensor, np.ndarray, DeviceArray],
) -> Union[torch.Tensor, np.ndarray, DeviceArray]:
    if torch.is_tensor(x) and torch.is_tensor(y):
        return torch.maximum(x, y)
    elif isinstance(x, DeviceArray) and isinstance(y, DeviceArray):
        return jnp.maximum(x, y)
    else:
        return np.maximum(x, y)


def squeeze(
    x: Union[torch.Tensor, np.ndarray, DeviceArray]
) -> Union[torch.Tensor, np.ndarray, DeviceArray]:
    if torch.is_tensor(x):
        return torch.squeeze(x)
    elif isinstance(x, DeviceArray):
        return jnp.squeeze(x)
    else:
        return np.squeeze(x)


def where(
    condition: Any,
    x: Union[torch.Tensor, np.ndarray, DeviceArray],
    y: Union[torch.Tensor, np.ndarray, DeviceArray],
) -> Union[torch.Tensor, np.ndarray, DeviceArray]:
    if torch.is_tensor(x) and torch.is_tensor(y):
        return torch.where(condition, x, y)
    elif isinstance(x, DeviceArray) and isinstance(y, DeviceArray):
        return jnp.where(condition, x, y)
    else:
        return np.where(condition, x, y)


def get_env_dimensions(info: dict, is_goalenv: bool, env) -> Dict[str, int]:
    """
    Return the important dimensions associated with an environment (observation_dim,
    action_dim, ...)
    """
    is_goalenv = is_goalenv
    if hasattr(env, "is_vector_env"):
        gymvecenv = env.is_vector_env
    else:
        gymvecenv = False
    dims = {}
    if gymvecenv:
        info["action_dim"] = env.single_action_space.shape[-1]
        info["observation_dim"] = (
            env.single_observation_space["observation"].shape[-1]
            if is_goalenv
            else env.single_observation_space.shape[-1]
        )
        info["achieved_goal_dim"] = (
            env.single_observation_space["achieved_goal"].shape[-1]
            if is_goalenv
            else None
        )
        info["desired_goal_dim"] = (
            env.single_observation_space["desired_goal"].shape[-1]
            if is_goalenv
            else None
        )
    else:
        info["action_dim"] = env.action_space.shape[-1]
        info["observation_dim"] = (
            env.observation_space["observation"].shape[-1]
            if is_goalenv
            else env.observation_space.shape[-1]
        )
        info["achieved_goal_dim"] = (
            env.observation_space["achieved_goal"].shape[-1] if is_goalenv else None
        )
        info["desired_goal_dim"] = (
            env.observation_space["desired_goal"].shape[-1] if is_goalenv else None
        )
    return dims
